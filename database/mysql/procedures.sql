-- Transactional stored procedures. Tested with MySQL 9.7.1.
-- They are optional for a future service layer, but executable and useful for atomic demonstrations.
SET NAMES utf8mb4;
USE food_platform;

DROP PROCEDURE IF EXISTS sp_record_audit_log;
DROP PROCEDURE IF EXISTS sp_deduct_inventory;
DROP PROCEDURE IF EXISTS sp_cancel_order_restore_inventory;
DROP PROCEDURE IF EXISTS sp_submit_product_audit;
DROP PROCEDURE IF EXISTS sp_create_order;

DELIMITER $$

CREATE PROCEDURE sp_record_audit_log(
  IN p_operator_user_id BIGINT UNSIGNED,
  IN p_operator_name VARCHAR(120),
  IN p_operation_type VARCHAR(64),
  IN p_object_type VARCHAR(48),
  IN p_object_code VARCHAR(80),
  IN p_before_value JSON,
  IN p_after_value JSON,
  IN p_reason VARCHAR(1000)
)
BEGIN
    IF p_operator_name IS NULL OR trim(p_operator_name) = '' OR p_operation_type IS NULL OR trim(p_operation_type) = ''
     OR p_object_type IS NULL OR trim(p_object_type) = '' OR p_object_code IS NULL OR trim(p_object_code) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'audit operator, operation, object type, and object code are required';
  END IF;
  INSERT INTO audit_log (
    audit_log_code, operator_user_id, operator_name_snapshot, operation_type,
    object_type, object_code, before_value, after_value, reason, operated_at
  ) VALUES (
    CONCAT('AL-', UUID_SHORT()), p_operator_user_id, p_operator_name, p_operation_type,
    p_object_type, p_object_code, p_before_value, p_after_value, p_reason, CURRENT_TIMESTAMP(3)
  );
END$$

CREATE PROCEDURE sp_deduct_inventory(
  IN p_spec_id BIGINT UNSIGNED,
  IN p_quantity INT UNSIGNED,
  IN p_business_code VARCHAR(64),
  IN p_operator_user_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_inventory_id BIGINT UNSIGNED;
  DECLARE v_before_qty INT UNSIGNED;
  DECLARE v_locked_qty INT UNSIGNED;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  IF p_spec_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'specification is required';
  END IF;
  IF p_quantity IS NULL OR p_quantity = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'deduct quantity must be greater than zero';
  END IF;
  IF p_business_code IS NULL OR trim(p_business_code) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'business code is required';
  END IF;

  START TRANSACTION;
  BEGIN
    DECLARE EXIT HANDLER FOR NOT FOUND
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'inventory record not found';
    SELECT id, available_qty, locked_qty INTO v_inventory_id, v_before_qty, v_locked_qty
    FROM product_inventory
    WHERE spec_id = p_spec_id AND warehouse_code = 'DEFAULT'
    FOR UPDATE;
  END;

  IF EXISTS (SELECT 1 FROM inventory_change_log
             WHERE inventory_id = v_inventory_id AND business_type = 'ORDER_DEDUCT' AND business_code = p_business_code) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'inventory has already been deducted for this business code';
  END IF;
  IF (v_before_qty - v_locked_qty) < p_quantity THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'insufficient sellable inventory';
  END IF;

  UPDATE product_inventory
  SET inventory_status = CASE
        WHEN (available_qty - p_quantity - locked_qty) = 0 THEN 'OUT_OF_STOCK'
        WHEN (available_qty - p_quantity - locked_qty) <= warning_threshold THEN 'LOW'
        ELSE 'NORMAL'
      END,
      available_qty = available_qty - p_quantity,
      version_no = version_no + 1
  WHERE id = v_inventory_id;

  INSERT INTO inventory_change_log (inventory_id,business_type,business_code,quantity_delta,before_qty,after_qty,operator_user_id,reason)
  VALUES (v_inventory_id,'ORDER_DEDUCT',p_business_code,-CAST(p_quantity AS SIGNED),v_before_qty,v_before_qty-p_quantity,p_operator_user_id,'订单扣减库存');
  COMMIT;
END$$

CREATE PROCEDURE sp_cancel_order_restore_inventory(
  IN p_order_no VARCHAR(40),
  IN p_operator_user_id BIGINT UNSIGNED,
  IN p_cancel_reason VARCHAR(500)
)
BEGIN
  DECLARE v_order_id BIGINT UNSIGNED;
  DECLARE v_order_status VARCHAR(24);
  DECLARE v_spec_id BIGINT UNSIGNED;
  DECLARE v_quantity INT UNSIGNED;
  DECLARE v_inventory_id BIGINT UNSIGNED;
  DECLARE v_before_qty INT UNSIGNED;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  IF p_order_no IS NULL OR trim(p_order_no) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order number is required';
  END IF;
  IF p_cancel_reason IS NULL OR trim(p_cancel_reason) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cancel reason is required';
  END IF;

  START TRANSACTION;
  BEGIN
    DECLARE EXIT HANDLER FOR NOT FOUND
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order not found';
    SELECT id, order_status INTO v_order_id, v_order_status
    FROM order_info WHERE order_no = p_order_no FOR UPDATE;
  END;

  IF EXISTS (
    SELECT 1 FROM inventory_change_log
    WHERE business_type = 'ORDER_RELEASE' AND business_code = p_order_no
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'inventory has already been restored';
  END IF;
  IF v_order_status IN ('COMPLETED', 'CANCELLED') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order status cannot be cancelled';
  END IF;

  BEGIN
    DECLARE v_done TINYINT DEFAULT 0;
    DECLARE cur_items CURSOR FOR
      SELECT spec_id, quantity
      FROM order_item
      WHERE order_id = v_order_id AND spec_id IS NOT NULL
      ORDER BY spec_id, id;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN cur_items;
    restore_loop: LOOP
      FETCH cur_items INTO v_spec_id, v_quantity;
      IF v_done = 1 THEN LEAVE restore_loop; END IF;

      BEGIN
        DECLARE EXIT HANDLER FOR NOT FOUND
          SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'inventory record not found while restoring order';
        SELECT id, available_qty INTO v_inventory_id, v_before_qty
        FROM product_inventory
        WHERE spec_id = v_spec_id AND warehouse_code = 'DEFAULT'
        FOR UPDATE;
      END;

      UPDATE product_inventory
      SET inventory_status = CASE
            WHEN (available_qty + v_quantity - locked_qty) <= warning_threshold THEN 'LOW'
            ELSE 'NORMAL'
          END,
          available_qty = available_qty + v_quantity,
          version_no = version_no + 1
      WHERE id = v_inventory_id;

      INSERT INTO inventory_change_log (
        inventory_id, business_type, business_code, quantity_delta,
        before_qty, after_qty, operator_user_id, reason
      ) VALUES (
        v_inventory_id, 'ORDER_RELEASE', p_order_no, CAST(v_quantity AS SIGNED),
        v_before_qty, v_before_qty + v_quantity, p_operator_user_id, p_cancel_reason
      );
    END LOOP;
    CLOSE cur_items;
  END;

  UPDATE order_info
  SET order_status = 'CANCELLED', cancelled_at = CURRENT_TIMESTAMP(3), cancel_reason = p_cancel_reason
  WHERE id = v_order_id;
  COMMIT;
END$$

CREATE PROCEDURE sp_submit_product_audit(
  IN p_product_code VARCHAR(40),
  IN p_submitter_user_id BIGINT UNSIGNED,
  IN p_product_version INT UNSIGNED,
  OUT p_audit_code VARCHAR(40)
)
BEGIN
  DECLARE v_product_id BIGINT UNSIGNED;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;

  IF p_product_code IS NULL OR trim(p_product_code) = '' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'product code is required';
  END IF;
  IF p_submitter_user_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'submitter is required';
  END IF;
  IF p_product_version IS NULL OR p_product_version = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'product version must be greater than zero';
  END IF;

  START TRANSACTION;
  BEGIN
    DECLARE EXIT HANDLER FOR NOT FOUND SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'product not found';
    SELECT id INTO v_product_id FROM product
    WHERE product_code = p_product_code AND is_deleted = 0 FOR UPDATE;
  END;

  IF EXISTS (SELECT 1 FROM product_audit
             WHERE product_id = v_product_id AND product_version = p_product_version
               AND audit_status IN ('PENDING','PROCESSING','TRANSFERRED','NEED_MORE_INFO')) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'an active audit already exists for this product version';
  END IF;

  SET p_audit_code = CONCAT('RV-', RIGHT(CONCAT('000000', UUID_SHORT()), 6));
  INSERT INTO product_audit (audit_code,product_id,product_version,audit_stage,audit_status,submitted_by,submitted_at)
  VALUES (p_audit_code,v_product_id,p_product_version,'FIELD_CHECK','PENDING',p_submitter_user_id,CURRENT_TIMESTAMP(3));
  UPDATE product SET review_status='PENDING',sale_status='DRAFT' WHERE id=v_product_id;
  INSERT INTO workflow_task (task_code,workflow_type,workflow_instance_code,business_type,business_code,node_code,node_name,task_status,candidate_role_code,payload_json,due_at)
  VALUES (CONCAT('WT-',UUID_SHORT()),'PRODUCT_AUDIT',p_audit_code,'PRODUCT',p_product_code,'FIELD_CHECK','字段校验','PENDING','PLATFORM_ADMIN',JSON_OBJECT('auditCode',p_audit_code,'productVersion',p_product_version),DATE_ADD(CURRENT_TIMESTAMP(3),INTERVAL 24 HOUR));
  COMMIT;
END$$

CREATE PROCEDURE sp_create_order(
  IN p_user_id BIGINT UNSIGNED,
  IN p_merchant_id BIGINT UNSIGNED,
  IN p_receiver_snapshot JSON,
  IN p_items JSON,
  IN p_buyer_remark VARCHAR(500),
  OUT p_order_no VARCHAR(40)
)
BEGIN
  DECLARE v_order_id BIGINT UNSIGNED;
  DECLARE v_goods_amount DECIMAL(14,2);
  DECLARE v_input_count INT DEFAULT 0;
  DECLARE v_distinct_spec_count INT DEFAULT 0;
  DECLARE v_invalid_input_count INT DEFAULT 0;
  DECLARE v_item_count INT DEFAULT 0;
  DECLARE v_invalid_count INT DEFAULT 0;
  DECLARE v_locked_count INT DEFAULT 0;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
    RESIGNAL;
  END;

  IF p_user_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'user is required';
  END IF;
  IF p_merchant_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'merchant is required';
  END IF;
  IF p_receiver_snapshot IS NULL OR JSON_TYPE(p_receiver_snapshot) <> 'OBJECT' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'receiver snapshot must be a JSON object';
  END IF;
  IF p_items IS NULL OR JSON_TYPE(p_items) <> 'ARRAY' OR JSON_LENGTH(p_items) = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order items cannot be empty';
  END IF;

  SELECT COUNT(*), COUNT(DISTINCT input.spec_id),
         SUM(CASE WHEN input.spec_id IS NULL OR input.quantity IS NULL OR input.quantity = 0 THEN 1 ELSE 0 END)
    INTO v_input_count, v_distinct_spec_count, v_invalid_input_count
  FROM JSON_TABLE(p_items, '$[*]' COLUMNS (
    spec_id BIGINT UNSIGNED PATH '$.spec_id' NULL ON EMPTY NULL ON ERROR,
    quantity INT UNSIGNED PATH '$.quantity' NULL ON EMPTY NULL ON ERROR
  )) AS input;
  IF v_invalid_input_count > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'specification is required and quantity must be greater than zero';
  END IF;
  IF v_input_count <> v_distinct_spec_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'duplicate specification in order items';
  END IF;

  START TRANSACTION;
  DROP TEMPORARY TABLE IF EXISTS tmp_order_items;
  CREATE TEMPORARY TABLE tmp_order_items (
    product_id BIGINT UNSIGNED NOT NULL,
    spec_id BIGINT UNSIGNED NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    product_code VARCHAR(40) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    spec_code VARCHAR(48) NOT NULL,
    spec_name VARCHAR(160) NOT NULL,
    image_url VARCHAR(1024) NULL,
    ingredient_version INT UNSIGNED NULL,
    PRIMARY KEY (spec_id)
  ) ENGINE=InnoDB;

  INSERT INTO tmp_order_items (
    product_id, spec_id, quantity, unit_price, product_code, product_name,
    spec_code, spec_name, image_url, ingredient_version
  )
  SELECT
    p.id, s.id, jt.quantity, price.amount, p.product_code, p.product_name,
    s.spec_code, s.spec_name,
    (SELECT image.image_url FROM product_image image
     WHERE image.product_id = p.id AND image.image_type = 'MAIN' AND image.status = 'ACTIVE'
     ORDER BY image.sort_order, image.id LIMIT 1),
    (SELECT MAX(snapshot.version_no) FROM product_ingredient_snapshot snapshot WHERE snapshot.product_id = p.id)
  FROM JSON_TABLE(p_items, '$[*]' COLUMNS (
    spec_id BIGINT UNSIGNED PATH '$.spec_id' ERROR ON EMPTY ERROR ON ERROR,
    quantity INT UNSIGNED PATH '$.quantity' ERROR ON EMPTY ERROR ON ERROR
  )) AS jt
  JOIN product_spec s ON s.id = jt.spec_id AND s.status = 'ACTIVE'
  JOIN product p ON p.id = s.product_id
    AND p.merchant_id = p_merchant_id
    AND p.sale_status = 'ON_SALE'
    AND p.review_status = 'APPROVED'
    AND p.is_deleted = 0
  JOIN product_price price ON price.spec_id = s.id
    AND price.price_type = 'SALE' AND price.status = 'ACTIVE'
    AND price.valid_from <= CURRENT_TIMESTAMP(3)
    AND (price.valid_to IS NULL OR price.valid_to > CURRENT_TIMESTAMP(3))
    AND price.valid_from = (
      SELECT MAX(p2.valid_from)
      FROM product_price p2
      WHERE p2.spec_id = s.id
        AND p2.price_type = 'SALE'
        AND p2.status = 'ACTIVE'
        AND p2.valid_from <= CURRENT_TIMESTAMP(3)
        AND (p2.valid_to IS NULL OR p2.valid_to > CURRENT_TIMESTAMP(3))
    );

  SELECT COUNT(*) INTO v_item_count FROM tmp_order_items;
  IF v_item_count <> v_input_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'product, merchant, sale status, review status, specification, or price is invalid';
  END IF;

  SET v_locked_count = 0;
  BEGIN
    DECLARE v_lock_done TINYINT DEFAULT 0;
    DECLARE v_locked_inventory_id BIGINT UNSIGNED;
    DECLARE cur_inventory CURSOR FOR
      SELECT i.id
      FROM product_inventory i
      JOIN tmp_order_items t ON t.spec_id = i.spec_id
      WHERE i.warehouse_code = 'DEFAULT'
      ORDER BY i.id
      FOR UPDATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_lock_done = 1;
    OPEN cur_inventory;
    lock_loop: LOOP
      FETCH cur_inventory INTO v_locked_inventory_id;
      IF v_lock_done = 1 THEN LEAVE lock_loop; END IF;
      SET v_locked_count = v_locked_count + 1;
    END LOOP;
    CLOSE cur_inventory;
  END;
  IF v_locked_count <> v_item_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'inventory record not found';
  END IF;

  SELECT COUNT(*) INTO v_invalid_count
  FROM tmp_order_items t
  JOIN product_inventory i ON i.spec_id = t.spec_id AND i.warehouse_code = 'DEFAULT'
  WHERE (i.available_qty - i.locked_qty) < t.quantity;
  IF v_invalid_count > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'one or more specifications have insufficient inventory';
  END IF;

  SELECT SUM(unit_price * quantity) INTO v_goods_amount FROM tmp_order_items;
  SET p_order_no = CONCAT('ZW', DATE_FORMAT(CURRENT_TIMESTAMP(3), '%Y%m%d%H%i%s'), RIGHT(UUID_SHORT(), 4));
  INSERT INTO order_info (
    order_no, user_id, merchant_id, order_status, payment_status, receiver_snapshot,
    goods_amount, discount_amount, shipping_amount, payable_amount, paid_amount,
    buyer_remark, placed_at
  ) VALUES (
    p_order_no, p_user_id, p_merchant_id, 'PENDING_PAYMENT', 'UNPAID', p_receiver_snapshot,
    v_goods_amount, 0, 0, v_goods_amount, 0, p_buyer_remark, CURRENT_TIMESTAMP(3)
  );
  SET v_order_id = LAST_INSERT_ID();

  INSERT INTO order_item (
    order_id, order_item_code, product_id, spec_id, product_code_snapshot,
    product_name_snapshot, spec_code_snapshot, spec_name_snapshot, image_url_snapshot,
    unit_price, quantity, subtotal_amount, ingredient_version_snapshot
  )
  SELECT v_order_id, CONCAT('OI-', UUID_SHORT(), '-', spec_id), product_id, spec_id, product_code,
         product_name, spec_code, spec_name, image_url, unit_price, quantity,
         unit_price * quantity, ingredient_version
  FROM tmp_order_items;

  INSERT INTO inventory_change_log (
    inventory_id, business_type, business_code, quantity_delta,
    before_qty, after_qty, operator_user_id, reason
  )
  SELECT i.id, 'ORDER_DEDUCT', p_order_no, -CAST(t.quantity AS SIGNED),
         i.available_qty, i.available_qty - t.quantity, p_user_id, '创建订单扣减库存'
  FROM tmp_order_items t
  JOIN product_inventory i ON i.spec_id = t.spec_id AND i.warehouse_code = 'DEFAULT';

  UPDATE product_inventory i
  JOIN tmp_order_items t ON t.spec_id = i.spec_id
  SET i.inventory_status = CASE
        WHEN (i.available_qty - t.quantity - i.locked_qty) = 0 THEN 'OUT_OF_STOCK'
        WHEN (i.available_qty - t.quantity - i.locked_qty) <= i.warning_threshold THEN 'LOW'
        ELSE 'NORMAL'
      END,
      i.available_qty = i.available_qty - t.quantity,
      i.version_no = i.version_no + 1
  WHERE i.warehouse_code = 'DEFAULT';

  DROP TEMPORARY TABLE tmp_order_items;
  COMMIT;
END$$

DELIMITER ;
