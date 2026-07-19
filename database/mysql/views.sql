-- Common read models for MySQL 8.0.
SET NAMES utf8mb4;
USE food_platform;

CREATE OR REPLACE VIEW v_product_average_rating AS
SELECT
  p.id AS product_id,
  p.product_code,
  p.product_name,
  COUNT(r.id) AS review_count,
  ROUND(AVG(r.rating), 2) AS average_rating
FROM product p
LEFT JOIN product_review r
  ON r.product_id = p.id AND r.status = 'PUBLISHED'
WHERE p.is_deleted = 0
GROUP BY p.id, p.product_code, p.product_name;

CREATE OR REPLACE VIEW v_product_inventory AS
SELECT
  p.product_code,
  p.product_name,
  s.spec_code,
  s.spec_name,
  i.warehouse_code,
  i.available_qty,
  i.locked_qty,
  (i.available_qty - i.locked_qty) AS sellable_qty,
  i.warning_threshold,
  CASE
    WHEN (i.available_qty - i.locked_qty) = 0 THEN 'OUT_OF_STOCK'
    WHEN (i.available_qty - i.locked_qty) <= i.warning_threshold THEN 'LOW'
    ELSE 'NORMAL'
  END AS calculated_inventory_status,
  i.updated_at
FROM product_inventory i
JOIN product p ON p.id = i.product_id
JOIN product_spec s ON s.id = i.spec_id
WHERE p.is_deleted = 0 AND s.status = 'ACTIVE';

CREATE OR REPLACE VIEW v_product_detail AS
SELECT
  p.id AS product_id,
  p.product_code,
  p.product_name,
  p.subtitle,
  p.raw_ingredient_text,
  p.allergen_notice,
  p.match_status,
  p.match_reason,
  p.evidence_text,
  p.info_source,
  p.sale_status,
  p.review_status,
  p.neo4j_node_key,
  m.merchant_code,
  m.merchant_name,
  b.brand_code,
  b.brand_name,
  c.category_code,
  c.category_name,
  s.spec_code,
  s.spec_name,
  pp.amount AS current_price,
  pp.currency,
  pi.image_url AS main_image_url,
  inv.available_qty,
  inv.locked_qty,
  (inv.available_qty - inv.locked_qty) AS sellable_qty,
  rating.review_count,
  rating.average_rating,
  p.updated_at
FROM product p
JOIN merchant m ON m.id = p.merchant_id
JOIN brand b ON b.id = p.brand_id
JOIN category c ON c.id = p.category_id
LEFT JOIN product_spec s ON s.product_id = p.id AND s.is_default = 1 AND s.status = 'ACTIVE'
LEFT JOIN product_price pp ON pp.spec_id = s.id
  AND pp.price_type = 'SALE'
  AND pp.status = 'ACTIVE'
  AND pp.valid_from <= CURRENT_TIMESTAMP(3)
  AND (pp.valid_to IS NULL OR pp.valid_to > CURRENT_TIMESTAMP(3))
  AND pp.valid_from = (
    SELECT MAX(pp2.valid_from)
    FROM product_price pp2
    WHERE pp2.spec_id = s.id
      AND pp2.price_type = 'SALE'
      AND pp2.status = 'ACTIVE'
      AND pp2.valid_from <= CURRENT_TIMESTAMP(3)
      AND (pp2.valid_to IS NULL OR pp2.valid_to > CURRENT_TIMESTAMP(3))
  )
LEFT JOIN product_image pi ON pi.product_id = p.id AND pi.image_type = 'MAIN' AND pi.sort_order = 0 AND pi.status = 'ACTIVE'
LEFT JOIN product_inventory inv ON inv.spec_id = s.id AND inv.warehouse_code = 'DEFAULT'
LEFT JOIN v_product_average_rating rating ON rating.product_id = p.id
WHERE p.is_deleted = 0;

CREATE OR REPLACE VIEW v_user_order_summary AS
SELECT
  u.user_code,
  u.username,
  COUNT(o.id) AS order_count,
  SUM(CASE WHEN o.order_status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_order_count,
  SUM(CASE WHEN o.order_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_order_count,
  COALESCE(SUM(o.paid_amount), 0.00) AS total_paid_amount,
  MAX(o.placed_at) AS latest_order_at
FROM sys_user u
LEFT JOIN order_info o ON o.user_id = u.id
WHERE u.is_deleted = 0
GROUP BY u.id, u.user_code, u.username;

CREATE OR REPLACE VIEW v_product_audit_status AS
SELECT
  p.product_code,
  p.product_name,
  p.review_status AS product_review_status,
  pa.audit_code,
  pa.product_version,
  pa.audit_stage,
  pa.audit_status,
  pa.audit_opinion,
  pa.submitted_at,
  pa.audited_at,
  auditor.user_code AS auditor_user_code,
  auditor_profile.nickname AS auditor_name
FROM product p
LEFT JOIN product_audit pa ON pa.id = (
  SELECT MAX(pa2.id) FROM product_audit pa2 WHERE pa2.product_id = p.id
)
LEFT JOIN sys_user auditor ON auditor.id = pa.auditor_user_id
LEFT JOIN user_profile auditor_profile ON auditor_profile.user_id = auditor.id
WHERE p.is_deleted = 0;

CREATE OR REPLACE VIEW v_ai_filter_history AS
SELECT
  h.filter_code,
  u.user_code,
  profile.nickname,
  c.conversation_code,
  h.raw_query,
  h.parsed_conditions,
  h.hard_constraints,
  h.soft_preferences,
  h.pending_confirmations,
  h.result_count,
  h.execution_mode,
  h.parse_status,
  h.rule_result_summary,
  h.executed_at
FROM ai_filter_history h
JOIN sys_user u ON u.id = h.user_id
LEFT JOIN user_profile profile ON profile.user_id = u.id
LEFT JOIN ai_conversation c ON c.id = h.conversation_id
WHERE h.is_deleted = 0;
