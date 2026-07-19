-- FoodPlatform repeatable demonstration seed for MySQL 8.0.
-- All demo users use the TEST-ONLY bcrypt hash below. Test password: password
-- Hash: $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
SET NAMES utf8mb4;
SET time_zone = '+08:00';
USE food_platform;
START TRANSACTION;

INSERT INTO sys_user (id,user_code,username,password_hash,phone,email,user_type,status,last_login_at,password_changed_at,created_at,updated_at) VALUES
(1,'USR0001','linxiaoman','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001001','linxiaoman@example.test','CONSUMER','ACTIVE','2026-07-18 09:42:00.000','2026-06-01 10:00:00.000','2026-02-18 10:00:00.000','2026-07-18 09:42:00.000'),
(2,'USR0002','zhouyian','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001002','zhouyian@example.test','CONSUMER','ACTIVE',NULL,'2026-06-02 10:00:00.000','2026-03-01 10:00:00.000','2026-07-17 10:00:00.000'),
(3,'USR0003','chenzijin','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001003','chenzijin@example.test','CONSUMER','ACTIVE',NULL,'2026-06-03 10:00:00.000','2026-03-11 10:00:00.000','2026-07-17 10:00:00.000'),
(4,'USR0004','liangduo','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001004','liangduo@example.test','CONSUMER','ACTIVE',NULL,'2026-06-04 10:00:00.000','2026-03-20 10:00:00.000','2026-07-17 10:00:00.000'),
(5,'USR0005','wangzhiqiu','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001005','wangzhiqiu@example.test','CONSUMER','ACTIVE',NULL,'2026-06-05 10:00:00.000','2026-04-01 10:00:00.000','2026-07-17 10:00:00.000'),
(6,'USR0006','tanghe','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001006','tanghe@example.test','CONSUMER','ACTIVE',NULL,'2026-06-06 10:00:00.000','2026-04-10 10:00:00.000','2026-07-17 10:00:00.000'),
(7,'USR0007','xuwangshu','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13800001007','xuwangshu@example.test','CONSUMER','ACTIVE',NULL,'2026-06-07 10:00:00.000','2026-04-20 10:00:00.000','2026-07-17 10:00:00.000'),
(8,'MER0001','merchant_zhiwei','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13900002001','zhiwei@example.test','MERCHANT','ACTIVE',NULL,'2026-05-01 10:00:00.000','2025-11-06 10:00:00.000','2026-07-18 08:00:00.000'),
(9,'MER0002','merchant_green','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13900002002','green@example.test','MERCHANT','ACTIVE',NULL,'2026-05-02 10:00:00.000','2026-01-06 10:00:00.000','2026-07-17 08:00:00.000'),
(10,'MER0003','merchant_daily','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13900002003','daily@example.test','MERCHANT','ACTIVE',NULL,'2026-05-03 10:00:00.000','2026-02-06 10:00:00.000','2026-07-17 08:00:00.000'),
(11,'ADM0001','gulan_admin','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13700003001','gulan@example.test','ADMIN','ACTIVE','2026-07-18 09:42:00.000','2026-05-10 10:00:00.000','2025-06-18 10:00:00.000','2026-07-18 09:42:00.000'),
(12,'KNO0001','zhouyan_knowledge','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13700003002','zhouyan@example.test','KNOWLEDGE_ADMIN','ACTIVE',NULL,'2026-05-11 10:00:00.000','2025-08-21 10:00:00.000','2026-07-18 09:18:00.000'),
(13,'OPS0001','zhaoning_ops','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy','13700003003','zhaoning@example.test','OPS','ACTIVE',NULL,'2026-05-12 10:00:00.000','2025-09-01 10:00:00.000','2026-07-18 09:00:00.000')
ON DUPLICATE KEY UPDATE updated_at=VALUES(updated_at);

INSERT INTO sys_role (id,role_code,role_name,description,status) VALUES
(1,'CONSUMER','注册消费者','管理个人偏好、购物车和订单','ACTIVE'),
(2,'MERCHANT','商家','仅维护本商家商品和订单','ACTIVE'),
(3,'PLATFORM_ADMIN','平台管理员','商品审核、用户商家与订单监管','ACTIVE'),
(4,'KNOWLEDGE_ADMIN','知识管理员','维护图谱实体、关系和版本','ACTIVE'),
(5,'OPS','系统运维','日志、模型调用与故障监控','ACTIVE')
ON DUPLICATE KEY UPDATE role_name=VALUES(role_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO sys_permission (id,permission_code,permission_name,resource_type,description) VALUES
(1,'PRODUCT_READ','浏览商品','API','公开或登录用户读取商品'),
(2,'PREFERENCE_WRITE','维护个人偏好','API','仅本人'),
(3,'ORDER_WRITE','创建与维护本人订单','API','仅消费者本人'),
(4,'MERCHANT_PRODUCT_WRITE','维护本商家商品','API','商家数据隔离'),
(5,'PRODUCT_AUDIT','审核商品','API','平台管理员'),
(6,'KNOWLEDGE_WRITE','维护知识图谱','API','知识管理员'),
(7,'USER_ADMIN','用户商家管理','API','平台管理员'),
(8,'AUDIT_READ','读取审计日志','API','按角色范围'),
(9,'MODEL_MONITOR','模型调用监控','API','管理员与运维'),
(10,'WORKFLOW_ADMIN','工作流配置','API','平台管理员')
ON DUPLICATE KEY UPDATE permission_name=VALUES(permission_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO sys_user_role (id,user_id,role_id,granted_by) VALUES
(1,1,1,11),(2,2,1,11),(3,3,1,11),(4,4,1,11),(5,5,1,11),(6,6,1,11),(7,7,1,11),
(8,8,2,11),(9,9,2,11),(10,10,2,11),(11,11,3,11),(12,12,4,11),(13,13,5,11)
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO sys_role_permission (role_id,permission_id) VALUES
(1,1),(1,2),(1,3),(1,8),(2,1),(2,4),(2,8),(3,1),(3,5),(3,7),(3,8),(3,9),(3,10),
(4,1),(4,6),(4,8),(4,9),(5,8),(5,9)
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO user_profile (id,user_id,nickname,gender,birthday,preference_completion) VALUES
(1,1,'林小满','FEMALE','1998-05-12',82),(2,2,'周亦安',NULL,NULL,65),(3,3,'陈子衿',NULL,NULL,70),
(4,4,'梁朵',NULL,NULL,60),(5,5,'王知秋',NULL,NULL,55),(6,6,'唐禾',NULL,NULL,75),(7,7,'许望舒',NULL,NULL,40),
(8,8,'知味优选运营',NULL,NULL,0),(9,9,'绿色生活运营',NULL,NULL,0),(10,10,'每日食品运营',NULL,NULL,0),
(11,11,'顾岚',NULL,NULL,0),(12,12,'周研',NULL,NULL,0),(13,13,'赵宁',NULL,NULL,0)
ON DUPLICATE KEY UPDATE nickname=VALUES(nickname),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO user_address (id,address_code,user_id,receiver_name,receiver_phone,province,city,district,detail_address,is_default) VALUES
(1,'ADDR0001',1,'林小满','13800001001','上海市','上海市','徐汇区','虹桥路718号2栋1206',1),
(2,'ADDR0002',1,'林先生','13900002176','上海市','上海市','浦东新区','张江路88号A座前台',0),
(3,'ADDR0003',2,'周亦安','13800001002','江苏省','南京市','鼓楼区','中山北路66号',1),
(4,'ADDR0004',3,'陈子衿','13800001003','浙江省','杭州市','西湖区','文三路128号',1),
(5,'ADDR0005',4,'梁朵','13800001004','广东省','深圳市','南山区','科技园南区18号',1)
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO user_ingredient_preference (id,preference_code,user_id,preference_type,ingredient_code,ingredient_name,strength,is_enabled) VALUES
(1,'PREF0001',1,'EXCLUDE','ING002','花生',100,1),(2,'PREF0002',1,'EXCLUDE','ING003','花生粉',100,1),
(3,'PREF0003',1,'EXCLUDE','ING004','花生酱',100,1),(4,'PREF0004',1,'PREFER','ING001','燕麦',80,1),
(5,'PREF0005',1,'PREFER','ING019','藜麦',70,1),(6,'PREF0006',2,'EXCLUDE','ING014','乳糖',100,1),
(7,'PREF0007',3,'PREFER','ING006','大豆',60,1),(8,'PREF0008',4,'EXCLUDE','ING015','麸质',100,1)
ON DUPLICATE KEY UPDATE ingredient_name=VALUES(ingredient_name),strength=VALUES(strength),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO merchant (id,merchant_code,owner_user_id,merchant_name,license_no,contact_name,contact_phone,status,approved_by,approved_at) VALUES
(1,'MCH0001',8,'知味优选旗舰店','TEST-LICENSE-0001','顾禾','13900002001','ACTIVE',11,'2025-11-07 10:00:00.000'),
(2,'MCH0002',9,'绿色生活食品店','TEST-LICENSE-0002','叶青','13900002002','ACTIVE',11,'2026-01-07 10:00:00.000'),
(3,'MCH0003',10,'每日食品集合店','TEST-LICENSE-0003','宋然','13900002003','ACTIVE',11,'2026-02-07 10:00:00.000')
ON DUPLICATE KEY UPDATE merchant_name=VALUES(merchant_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO brand (id,brand_code,merchant_id,brand_name,neo4j_node_key,status) VALUES
(1,'BR001',1,'谷本日记','BR001','ACTIVE'),(2,'BR002',1,'欧扎克','BR002','ACTIVE'),(3,'BR003',3,'每日盒子','BR003','ACTIVE'),
(4,'BR004',2,'牧场清晨','BR004','ACTIVE'),(5,'BR005',2,'北海乳业','BR005','ACTIVE'),(6,'BR006',3,'坚果森林','BR006','ACTIVE'),
(7,'BR007',2,'橙意满满','BR007','ACTIVE'),(8,'BR008',3,'麦香工房','BR008','ACTIVE'),(9,'BR009',3,'可可宇宙','BR009','ACTIVE'),
(10,'BR010',1,'味原纪','BR010','ACTIVE'),(11,'BR011',1,'简食社','BR011','ACTIVE'),(12,'BR012',2,'植选研究所','BR012','ACTIVE'),
(13,'BR013',3,'山野集','BR013','ACTIVE'),(14,'BR014',1,'轻负担','BR014','ACTIVE'),(15,'BR015',1,'禾谷里','BR015','ACTIVE')
ON DUPLICATE KEY UPDATE brand_name=VALUES(brand_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO category (id,category_code,category_name,category_level,sort_order,status,neo4j_node_key) VALUES
(1,'CAT001','早餐麦片',1,1,'ACTIVE','CAT001'),(2,'CAT002','饼干糕点',1,2,'ACTIVE','CAT002'),
(3,'CAT003','乳品酸奶',1,3,'ACTIVE','CAT003'),(4,'CAT004','坚果果干',1,4,'ACTIVE','CAT004'),
(5,'CAT005','果汁饮品',1,5,'ACTIVE','CAT005'),(6,'CAT006','面包烘焙',1,6,'ACTIVE','CAT006'),
(7,'CAT007','巧克力',1,7,'ACTIVE','CAT007'),(8,'CAT008','调味速食',1,8,'ACTIVE','CAT008'),
(9,'CAT009','谷物能量棒',1,9,'ACTIVE','CAT009'),(10,'CAT010','植物蛋白',1,10,'ACTIVE','CAT010')
ON DUPLICATE KEY UPDATE category_name=VALUES(category_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product (id,product_code,merchant_id,brand_id,category_id,product_name,raw_ingredient_text,allergen_notice,match_status,match_reason,evidence_text,info_source,sale_status,review_status,neo4j_node_key,graph_sync_status,graph_version,created_at,updated_at) VALUES
(1,'FP0001',1,1,1,'原味低糖燕麦脆','全粒燕麦、藜麦、南瓜籽、椰子片、菊粉',NULL,'FULL_MATCH','不含已排除成分，糖含量较低，配料信息完整','商品标签未检出花生、花生粉或花生酱','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0001','SYNCED','v2.18.0','2026-05-01 10:00:00.000','2026-07-16 10:00:00.000'),
(2,'FP0002',1,2,1,'莓果奇亚籽谷物杯','燕麦片、草莓干、蓝莓干、奇亚籽、酸奶块；食品添加剂：磷脂','本生产线亦处理花生制品','RISK','主体配料未见花生，但标签提示同线生产可能含有花生','包装过敏原提示：“本生产线亦处理花生制品”','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0002','SYNCED','v2.18.0','2026-05-02 10:00:00.000','2026-07-16 10:00:00.000'),
(3,'FP0003',1,14,2,'海盐燕麦曲奇','小麦粉、燕麦、黄油、海盐、白砂糖',NULL,'NOT_MATCH','糖含量高于当前偏好上限','营养标签：糖 14.8g/100g','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0003','SYNCED','v2.18.0','2026-05-03 10:00:00.000','2026-07-16 10:00:00.000'),
(4,'FP0004',1,4,3,'有机全脂鲜牛奶','生牛乳',NULL,'FULL_MATCH','单一配料，无食品添加剂','原始配料表仅含“生牛乳”','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0004','SYNCED','v2.18.0','2026-05-04 10:00:00.000','2026-07-16 10:00:00.000'),
(5,'FP0005',1,5,3,'希腊式原味酸奶','生牛乳、嗜热链球菌、保加利亚乳杆菌',NULL,'FULL_MATCH','不含已排除成分，配料信息完整','商品标签未检出花生及其制品','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0005','SYNCED','v2.18.0','2026-05-05 10:00:00.000','2026-07-16 10:00:00.000'),
(6,'FP0006',1,6,4,'每日原味混合坚果','巴旦木、腰果、核桃、榛子、蔓越莓干','可能含有花生','RISK','含多种树坚果，且存在花生交叉接触风险','商品标签过敏原信息','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0006','SYNCED','v2.18.0','2026-05-06 10:00:00.000','2026-07-16 10:00:00.000'),
(7,'FP0007',1,7,5,'NFC鲜榨橙汁','橙汁',NULL,'FULL_MATCH','单一果汁配料','原始配料表仅含“橙汁”','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0007','SYNCED','v2.18.0','2026-05-07 10:00:00.000','2026-07-16 10:00:00.000'),
(8,'FP0008',1,8,6,'全麦核桃软欧包','全麦粉、小麦粉、核桃、酵母、海盐；食品添加剂：抗坏血酸',NULL,'FULL_MATCH','配料信息完整','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0008','SYNCED','v2.18.0','2026-05-08 10:00:00.000','2026-07-16 10:00:00.000'),
(9,'FP0009',1,9,7,'72%黑巧克力薄片','可可液块、可可脂、赤藓糖醇、白砂糖；食品添加剂：大豆磷脂','可能含有牛奶、坚果','RISK','可能含牛奶与坚果，需结合个人排除条件确认','包装“可能含有”区域','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0009','SYNCED','v2.18.0','2026-05-09 10:00:00.000','2026-07-16 10:00:00.000'),
(10,'FP0010',1,10,8,'零添加番茄意面酱','番茄、洋葱、橄榄油、罗勒、海盐',NULL,'FULL_MATCH','无食品添加剂，配料简单','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0010','SYNCED','v2.18.0','2026-05-10 10:00:00.000','2026-07-16 10:00:00.000'),
(11,'FP0011',1,11,8,'藜麦鸡肉暖食碗','藜麦、鸡胸肉、玉米、胡萝卜、西兰花；食品添加剂：乳酸钠',NULL,'FULL_MATCH','蛋白质较高，配料信息完整','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0011','SYNCED','v2.18.0','2026-05-11 10:00:00.000','2026-07-16 10:00:00.000'),
(12,'FP0012',1,15,9,'海盐黑巧谷物棒','燕麦、黑巧克力、麦芽糖浆、杏仁、海盐；食品添加剂：大豆磷脂',NULL,'NOT_MATCH','含杏仁且糖含量高于偏好','配料表与营养标签双重命中','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0012','SYNCED','v2.18.0','2026-05-12 10:00:00.000','2026-07-16 10:00:00.000'),
(13,'FP0013',1,12,10,'无糖高蛋白豆乳','水、非转基因大豆；食品添加剂：碳酸钙、维生素D',NULL,'FULL_MATCH','无添加糖，蛋白质来源明确','营养标签糖为0g/100mL','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0013','SYNCED','v2.18.0','2026-05-13 10:00:00.000','2026-07-16 10:00:00.000'),
(14,'FP0014',1,12,10,'燕麦植物奶','水、燕麦、菜籽油、海盐；食品添加剂：磷酸氢二钾',NULL,'FULL_MATCH','植物基配方，信息完整','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0014','SYNCED','v2.18.0','2026-05-14 10:00:00.000','2026-07-16 10:00:00.000'),
(15,'FP0015',1,13,2,'桂花小米酥','小米、糯米、桂花、麦芽糖、复配谷物粉',NULL,'INFORMATION_INSUFFICIENT','“复配谷物粉”缺少展开成分，无法判定全部来源','原始标签未披露复配配料构成','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0015','SYNCED','v2.18.0','2026-05-15 10:00:00.000','2026-07-16 10:00:00.000'),
(16,'FP0016',1,1,1,'肉桂苹果烤燕麦','全粒燕麦、苹果干、肉桂、葵花籽、枫糖浆',NULL,'FULL_MATCH','配料信息完整','商品标签未检出花生及其制品','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0016','SYNCED','v2.18.0','2026-05-16 10:00:00.000','2026-07-16 10:00:00.000'),
(17,'FP0017',1,3,2,'原味花生酱夹心饼','小麦粉、花生酱、白砂糖、植物油',NULL,'NOT_MATCH','明确含有用户排除的花生酱','原始配料表第2项：花生酱','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0017','SYNCED','v2.18.0','2026-05-17 10:00:00.000','2026-07-16 10:00:00.000'),
(18,'FP0018',1,5,3,'草莓谷物轻酸奶','生牛乳、草莓果酱、燕麦脆、乳酸菌；食品添加剂：果胶',NULL,'FULL_MATCH','配料信息完整','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0018','SYNCED','v2.18.0','2026-05-18 10:00:00.000','2026-07-16 10:00:00.000'),
(19,'FP0019',1,14,2,'芝麻海苔苏打饼干','小麦粉、黑芝麻、海苔、酵母、海盐；食品添加剂：碳酸氢钠',NULL,'FULL_MATCH','糖含量较低','营养标签：糖2.8g/100g','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0019','SYNCED','v2.18.0','2026-05-19 10:00:00.000','2026-07-16 10:00:00.000'),
(20,'FP0020',1,11,8,'低钠菌菇汤面','小麦粉、香菇、杏鲍菇、酱油粉、葱；食品添加剂：谷氨酸钠、呈味核苷酸二钠',NULL,'FULL_MATCH','配料信息完整','原始标签与结构化映射一致','商品包装标签 · 商家提交 · 平台人工复核','ON_SALE','APPROVED','FP0020','SYNCED','v2.18.0','2026-05-20 10:00:00.000','2026-07-16 10:00:00.000')
ON DUPLICATE KEY UPDATE product_name=VALUES(product_name),raw_ingredient_text=VALUES(raw_ingredient_text),updated_at=VALUES(updated_at);

INSERT INTO product_spec (id,spec_code,product_id,spec_name,unit_name,status,is_default) VALUES
(1,'SPEC-FP0001-01',1,'400g/袋','袋','ACTIVE',1),(2,'SPEC-FP0002-01',2,'400g/袋','袋','ACTIVE',1),
(3,'SPEC-FP0003-01',3,'400g/袋','袋','ACTIVE',1),(4,'SPEC-FP0004-01',4,'250mL×10盒','箱','ACTIVE',1),
(5,'SPEC-FP0005-01',5,'120g×6杯','组','ACTIVE',1),(6,'SPEC-FP0006-01',6,'25g×14袋','盒','ACTIVE',1),
(7,'SPEC-FP0007-01',7,'300mL×4瓶','组','ACTIVE',1),(8,'SPEC-FP0008-01',8,'400g/袋','袋','ACTIVE',1),
(9,'SPEC-FP0009-01',9,'100g/盒','盒','ACTIVE',1),(10,'SPEC-FP0010-01',10,'400g/袋','袋','ACTIVE',1),
(11,'SPEC-FP0011-01',11,'280g/盒','盒','ACTIVE',1),(12,'SPEC-FP0012-01',12,'30g×6条','盒','ACTIVE',1),
(13,'SPEC-FP0013-01',13,'250mL×8盒','箱','ACTIVE',1),(14,'SPEC-FP0014-01',14,'1L/盒','盒','ACTIVE',1),
(15,'SPEC-FP0015-01',15,'400g/袋','袋','ACTIVE',1),(16,'SPEC-FP0016-01',16,'400g/袋','袋','ACTIVE',1),
(17,'SPEC-FP0017-01',17,'400g/袋','袋','ACTIVE',1),(18,'SPEC-FP0018-01',18,'180g×4杯','组','ACTIVE',1),
(19,'SPEC-FP0019-01',19,'400g/袋','袋','ACTIVE',1),(20,'SPEC-FP0020-01',20,'92g/杯','杯','ACTIVE',1)
ON DUPLICATE KEY UPDATE spec_name=VALUES(spec_name),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product_image (id,product_id,spec_id,image_type,image_url,alt_text,sort_order,status) VALUES
(1,1,1,'MAIN','https://images.unsplash.com/photo-1517673400267-0251440c45dc?auto=format&fit=crop&w=900&q=82','原味低糖燕麦脆',0,'ACTIVE'),
(2,2,2,'MAIN','https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=900&q=82','莓果奇亚籽谷物杯',0,'ACTIVE'),
(3,3,3,'MAIN','https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=900&q=82','海盐燕麦曲奇',0,'ACTIVE'),
(4,4,4,'MAIN','https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=900&q=82','有机全脂鲜牛奶',0,'ACTIVE'),
(5,5,5,'MAIN','https://images.unsplash.com/photo-1571212515416-fca77afa8caa?auto=format&fit=crop&w=900&q=82','希腊式原味酸奶',0,'ACTIVE'),
(6,6,6,'MAIN','https://images.unsplash.com/photo-1599599810694-b5b37304c041?auto=format&fit=crop&w=900&q=82','每日原味混合坚果',0,'ACTIVE'),
(7,7,7,'MAIN','https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=900&q=82','NFC鲜榨橙汁',0,'ACTIVE'),
(8,8,8,'MAIN','https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=82','全麦核桃软欧包',0,'ACTIVE'),
(9,9,9,'MAIN','https://images.unsplash.com/photo-1575377427642-087cf684f29d?auto=format&fit=crop&w=900&q=82','72%黑巧克力薄片',0,'ACTIVE'),
(10,10,10,'MAIN','https://images.unsplash.com/photo-1472476443507-c7a5948772fc?auto=format&fit=crop&w=900&q=82','零添加番茄意面酱',0,'ACTIVE'),
(11,11,11,'MAIN','https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=82','藜麦鸡肉暖食碗',0,'ACTIVE'),
(12,12,12,'MAIN','https://images.unsplash.com/photo-1571748982800-fa51082c2224?auto=format&fit=crop&w=900&q=82','海盐黑巧谷物棒',0,'ACTIVE'),
(13,13,13,'MAIN','https://images.unsplash.com/photo-1556881286-fc6915169721?auto=format&fit=crop&w=900&q=82','无糖高蛋白豆乳',0,'ACTIVE'),
(14,14,14,'MAIN','https://images.unsplash.com/photo-1600788907416-456578634209?auto=format&fit=crop&w=900&q=82','燕麦植物奶',0,'ACTIVE'),
(15,15,15,'MAIN','https://images.unsplash.com/photo-1587241321921-91a834d6d191?auto=format&fit=crop&w=900&q=82','桂花小米酥',0,'ACTIVE'),
(16,16,16,'MAIN','https://images.unsplash.com/photo-1517093157656-b9eccef91cb1?auto=format&fit=crop&w=900&q=82','肉桂苹果烤燕麦',0,'ACTIVE'),
(17,17,17,'MAIN','https://images.unsplash.com/photo-1559622214-f8a9850965bb?auto=format&fit=crop&w=900&q=82','原味花生酱夹心饼',0,'ACTIVE'),
(18,18,18,'MAIN','https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=900&q=82','草莓谷物轻酸奶',0,'ACTIVE'),
(19,19,19,'MAIN','https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=900&q=82','芝麻海苔苏打饼干',0,'ACTIVE'),
(20,20,20,'MAIN','https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=900&q=82','低钠菌菇汤面',0,'ACTIVE')
ON DUPLICATE KEY UPDATE image_url=VALUES(image_url),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product_price (id,product_id,spec_id,price_type,amount,currency,valid_from,status) VALUES
(1,1,1,'SALE',36.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(2,2,2,'SALE',29.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(3,3,3,'SALE',24.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(4,4,4,'SALE',59.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(5,5,5,'SALE',42.00,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(6,6,6,'SALE',49.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(7,7,7,'SALE',32.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(8,8,8,'SALE',22.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(9,9,9,'SALE',39.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(10,10,10,'SALE',26.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(11,11,11,'SALE',31.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(12,12,12,'SALE',28.50,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(13,13,13,'SALE',46.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(14,14,14,'SALE',34.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(15,15,15,'SALE',19.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(16,16,16,'SALE',39.50,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(17,17,17,'SALE',16.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(18,18,18,'SALE',35.80,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(19,19,19,'SALE',21.90,'CNY','2026-01-01 00:00:00.000','ACTIVE'),(20,20,20,'SALE',18.50,'CNY','2026-01-01 00:00:00.000','ACTIVE'),
(21,1,1,'LIST',42.90,'CNY','2026-01-01 00:00:00.000','ACTIVE')
ON DUPLICATE KEY UPDATE amount=VALUES(amount),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product_inventory (id,product_id,spec_id,warehouse_code,available_qty,locked_qty,warning_threshold,inventory_status) VALUES
(1,1,1,'DEFAULT',85,0,10,'NORMAL'),(2,2,2,'DEFAULT',85,0,10,'NORMAL'),(3,3,3,'DEFAULT',85,0,10,'NORMAL'),
(4,4,4,'DEFAULT',85,0,10,'NORMAL'),(5,5,5,'DEFAULT',85,0,10,'NORMAL'),(6,6,6,'DEFAULT',85,0,10,'NORMAL'),
(7,7,7,'DEFAULT',85,0,10,'NORMAL'),(8,8,8,'DEFAULT',8,0,10,'LOW'),(9,9,9,'DEFAULT',85,0,10,'NORMAL'),
(10,10,10,'DEFAULT',85,0,10,'NORMAL'),(11,11,11,'DEFAULT',85,0,10,'NORMAL'),(12,12,12,'DEFAULT',85,0,10,'NORMAL'),
(13,13,13,'DEFAULT',85,0,10,'NORMAL'),(14,14,14,'DEFAULT',85,0,10,'NORMAL'),(15,15,15,'DEFAULT',85,0,10,'NORMAL'),
(16,16,16,'DEFAULT',85,0,10,'NORMAL'),(17,17,17,'DEFAULT',85,0,10,'NORMAL'),(18,18,18,'DEFAULT',85,0,10,'NORMAL'),
(19,19,19,'DEFAULT',85,0,10,'NORMAL'),(20,20,20,'DEFAULT',85,0,10,'NORMAL')
ON DUPLICATE KEY UPDATE available_qty=VALUES(available_qty),inventory_status=VALUES(inventory_status),updated_at=CURRENT_TIMESTAMP(3);

-- Structured ingredients are separate from product.raw_ingredient_text and use Neo4j business codes.
INSERT INTO product_ingredient_snapshot (snapshot_code,product_id,spec_id,version_no,entity_type,entity_code,normalized_name,relation_type,raw_fragment,confidence,source_code,audit_status,graph_sync_status) VALUES
('PIS0001',1,1,1,'INGREDIENT','ING001','燕麦','CONTAINS','全粒燕麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0002',1,1,1,'INGREDIENT','ING019','藜麦','CONTAINS','藜麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0003',1,1,1,'INGREDIENT','ING020','南瓜籽','CONTAINS','南瓜籽',0.99,'SRC001','APPROVED','SYNCED'),('PIS0004',1,1,1,'INGREDIENT','ING037','椰子片','CONTAINS','椰子片',0.98,'SRC001','APPROVED','SYNCED'),('PIS0005',1,1,1,'INGREDIENT','ING030','菊粉','CONTAINS','菊粉',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0006',2,2,1,'INGREDIENT','ING001','燕麦','CONTAINS','燕麦片',0.98,'SRC001','APPROVED','SYNCED'),('PIS0007',2,2,1,'INGREDIENT','ING028','草莓','CONTAINS','草莓干',0.95,'SRC001','APPROVED','SYNCED'),('PIS0008',2,2,1,'INGREDIENT','ING029','蓝莓','CONTAINS','蓝莓干',0.95,'SRC001','APPROVED','SYNCED'),('PIS0009',2,2,1,'INGREDIENT','ING018','奇亚籽','CONTAINS','奇亚籽',0.99,'SRC001','APPROVED','SYNCED'),('PIS0010',2,2,1,'ADDITIVE','ADD001','磷脂','CONTAINS','磷脂',0.99,'SRC001','APPROVED','SYNCED'),('PIS0011',2,2,1,'INGREDIENT','ING002','花生','MAY_CONTAIN','可能含有花生',1.00,'SRC001','APPROVED','SYNCED'),
('PIS0012',3,3,1,'INGREDIENT','ING007','小麦','CONTAINS','小麦粉',0.99,'SRC001','APPROVED','SYNCED'),('PIS0013',3,3,1,'INGREDIENT','ING001','燕麦','CONTAINS','燕麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0014',3,3,1,'INGREDIENT','ING038','黄油','CONTAINS','黄油',0.99,'SRC001','APPROVED','SYNCED'),('PIS0015',3,3,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),('PIS0016',3,3,1,'INGREDIENT','ING016','白砂糖','CONTAINS','白砂糖',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0017',4,4,1,'INGREDIENT','ING005','牛奶','CONTAINS','生牛乳',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0018',5,5,1,'INGREDIENT','ING005','牛奶','CONTAINS','生牛乳',0.99,'SRC001','APPROVED','SYNCED'),('PIS0019',5,5,1,'INGREDIENT','ING039','嗜热链球菌','CONTAINS','嗜热链球菌',0.98,'SRC001','APPROVED','SYNCED'),('PIS0020',5,5,1,'INGREDIENT','ING040','保加利亚乳杆菌','CONTAINS','保加利亚乳杆菌',0.98,'SRC001','APPROVED','SYNCED'),
('PIS0021',6,6,1,'INGREDIENT','ING010','杏仁','CONTAINS','巴旦木',0.97,'SRC001','APPROVED','SYNCED'),('PIS0022',6,6,1,'INGREDIENT','ING011','腰果','CONTAINS','腰果',0.99,'SRC001','APPROVED','SYNCED'),('PIS0023',6,6,1,'INGREDIENT','ING012','核桃','CONTAINS','核桃',0.99,'SRC001','APPROVED','SYNCED'),('PIS0024',6,6,1,'INGREDIENT','ING013','榛子','CONTAINS','榛子',0.99,'SRC001','APPROVED','SYNCED'),('PIS0025',6,6,1,'INGREDIENT','ING041','蔓越莓','CONTAINS','蔓越莓干',0.96,'SRC001','APPROVED','SYNCED'),('PIS0026',6,6,1,'INGREDIENT','ING002','花生','MAY_CONTAIN','可能含有花生',1.00,'SRC001','APPROVED','SYNCED'),
('PIS0027',7,7,1,'INGREDIENT','ING042','橙汁','CONTAINS','橙汁',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0028',8,8,1,'INGREDIENT','ING007','小麦','CONTAINS','全麦粉',0.98,'SRC001','APPROVED','SYNCED'),('PIS0029',8,8,1,'INGREDIENT','ING012','核桃','CONTAINS','核桃',0.99,'SRC001','APPROVED','SYNCED'),('PIS0030',8,8,1,'INGREDIENT','ING032','酵母','CONTAINS','酵母',0.99,'SRC001','APPROVED','SYNCED'),('PIS0031',8,8,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),('PIS0032',8,8,1,'ADDITIVE','ADD004','抗坏血酸','CONTAINS','抗坏血酸',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0033',9,9,1,'INGREDIENT','ING022','可可液块','CONTAINS','可可液块',0.99,'SRC001','APPROVED','SYNCED'),('PIS0034',9,9,1,'INGREDIENT','ING023','可可脂','CONTAINS','可可脂',0.99,'SRC001','APPROVED','SYNCED'),('PIS0035',9,9,1,'INGREDIENT','ING017','赤藓糖醇','CONTAINS','赤藓糖醇',0.99,'SRC001','APPROVED','SYNCED'),('PIS0036',9,9,1,'INGREDIENT','ING016','白砂糖','CONTAINS','白砂糖',0.99,'SRC001','APPROVED','SYNCED'),('PIS0037',9,9,1,'ADDITIVE','ADD002','大豆磷脂','CONTAINS','大豆磷脂',0.99,'SRC001','APPROVED','SYNCED'),('PIS0038',9,9,1,'INGREDIENT','ING005','牛奶','MAY_CONTAIN','可能含有牛奶',1.00,'SRC001','APPROVED','SYNCED'),('PIS0039',9,9,1,'INGREDIENT','ING058','坚果','MAY_CONTAIN','可能含有坚果',1.00,'SRC001','APPROVED','SYNCED'),
('PIS0040',10,10,1,'INGREDIENT','ING024','番茄','CONTAINS','番茄',0.99,'SRC001','APPROVED','SYNCED'),('PIS0041',10,10,1,'INGREDIENT','ING025','洋葱','CONTAINS','洋葱',0.99,'SRC001','APPROVED','SYNCED'),('PIS0042',10,10,1,'INGREDIENT','ING026','橄榄油','CONTAINS','橄榄油',0.99,'SRC001','APPROVED','SYNCED'),('PIS0043',10,10,1,'INGREDIENT','ING035','罗勒','CONTAINS','罗勒',0.99,'SRC001','APPROVED','SYNCED'),('PIS0044',10,10,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0045',11,11,1,'INGREDIENT','ING019','藜麦','CONTAINS','藜麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0046',11,11,1,'INGREDIENT','ING027','鸡胸肉','CONTAINS','鸡胸肉',0.99,'SRC001','APPROVED','SYNCED'),('PIS0047',11,11,1,'INGREDIENT','ING036','玉米','CONTAINS','玉米',0.99,'SRC001','APPROVED','SYNCED'),('PIS0048',11,11,1,'INGREDIENT','ING059','胡萝卜','CONTAINS','胡萝卜',0.99,'SRC001','APPROVED','SYNCED'),('PIS0049',11,11,1,'INGREDIENT','ING060','西兰花','CONTAINS','西兰花',0.99,'SRC001','APPROVED','SYNCED'),('PIS0050',11,11,1,'ADDITIVE','ADD005','乳酸钠','CONTAINS','乳酸钠',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0051',12,12,1,'INGREDIENT','ING001','燕麦','CONTAINS','燕麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0052',12,12,1,'INGREDIENT','ING022','可可液块','CONTAINS','黑巧克力',0.95,'SRC001','APPROVED','SYNCED'),('PIS0053',12,12,1,'INGREDIENT','ING043','麦芽糖浆','CONTAINS','麦芽糖浆',0.99,'SRC001','APPROVED','SYNCED'),('PIS0054',12,12,1,'INGREDIENT','ING010','杏仁','CONTAINS','杏仁',0.99,'SRC001','APPROVED','SYNCED'),('PIS0055',12,12,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),('PIS0056',12,12,1,'ADDITIVE','ADD002','大豆磷脂','CONTAINS','大豆磷脂',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0057',13,13,1,'INGREDIENT','ING044','水','CONTAINS','水',0.99,'SRC001','APPROVED','SYNCED'),('PIS0058',13,13,1,'INGREDIENT','ING006','大豆','CONTAINS','非转基因大豆',0.99,'SRC001','APPROVED','SYNCED'),('PIS0059',13,13,1,'ADDITIVE','ADD006','碳酸钙','CONTAINS','碳酸钙',0.99,'SRC001','APPROVED','SYNCED'),('PIS0060',13,13,1,'ADDITIVE','ADD007','维生素D','CONTAINS','维生素D',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0061',14,14,1,'INGREDIENT','ING044','水','CONTAINS','水',0.99,'SRC001','APPROVED','SYNCED'),('PIS0062',14,14,1,'INGREDIENT','ING001','燕麦','CONTAINS','燕麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0063',14,14,1,'INGREDIENT','ING045','菜籽油','CONTAINS','菜籽油',0.99,'SRC001','APPROVED','SYNCED'),('PIS0064',14,14,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),('PIS0065',14,14,1,'ADDITIVE','ADD008','磷酸氢二钾','CONTAINS','磷酸氢二钾',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0066',15,15,1,'INGREDIENT','ING046','小米','CONTAINS','小米',0.99,'SRC001','APPROVED','SYNCED'),('PIS0067',15,15,1,'INGREDIENT','ING047','糯米','CONTAINS','糯米',0.99,'SRC001','APPROVED','SYNCED'),('PIS0068',15,15,1,'INGREDIENT','ING048','桂花','CONTAINS','桂花',0.99,'SRC001','APPROVED','SYNCED'),('PIS0069',15,15,1,'INGREDIENT','ING049','麦芽糖','CONTAINS','麦芽糖',0.99,'SRC001','APPROVED','SYNCED'),('PIS0070',15,15,1,'UNKNOWN','UNK001','复配谷物粉','UNKNOWN','复配谷物粉',NULL,'SRC001','PENDING','PENDING'),
('PIS0071',16,16,1,'INGREDIENT','ING001','燕麦','CONTAINS','全粒燕麦',0.99,'SRC001','APPROVED','SYNCED'),('PIS0072',16,16,1,'INGREDIENT','ING033','苹果','CONTAINS','苹果干',0.97,'SRC001','APPROVED','SYNCED'),('PIS0073',16,16,1,'INGREDIENT','ING034','肉桂','CONTAINS','肉桂',0.99,'SRC001','APPROVED','SYNCED'),('PIS0074',16,16,1,'INGREDIENT','ING021','葵花籽','CONTAINS','葵花籽',0.99,'SRC001','APPROVED','SYNCED'),('PIS0075',16,16,1,'INGREDIENT','ING050','枫糖浆','CONTAINS','枫糖浆',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0076',17,17,1,'INGREDIENT','ING007','小麦','CONTAINS','小麦粉',0.99,'SRC001','APPROVED','SYNCED'),('PIS0077',17,17,1,'INGREDIENT','ING004','花生酱','CONTAINS','花生酱',0.99,'SRC001','APPROVED','SYNCED'),('PIS0078',17,17,1,'INGREDIENT','ING016','白砂糖','CONTAINS','白砂糖',0.99,'SRC001','APPROVED','SYNCED'),('PIS0079',17,17,1,'INGREDIENT','ING051','植物油','CONTAINS','植物油',0.96,'SRC001','APPROVED','SYNCED'),
('PIS0080',18,18,1,'INGREDIENT','ING005','牛奶','CONTAINS','生牛乳',0.99,'SRC001','APPROVED','SYNCED'),('PIS0081',18,18,1,'INGREDIENT','ING028','草莓','CONTAINS','草莓果酱',0.95,'SRC001','APPROVED','SYNCED'),('PIS0082',18,18,1,'INGREDIENT','ING001','燕麦','CONTAINS','燕麦脆',0.95,'SRC001','APPROVED','SYNCED'),('PIS0083',18,18,1,'INGREDIENT','ING052','乳酸菌','CONTAINS','乳酸菌',0.99,'SRC001','APPROVED','SYNCED'),('PIS0084',18,18,1,'ADDITIVE','ADD003','果胶','CONTAINS','果胶',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0085',19,19,1,'INGREDIENT','ING007','小麦','CONTAINS','小麦粉',0.99,'SRC001','APPROVED','SYNCED'),('PIS0086',19,19,1,'INGREDIENT','ING009','芝麻','CONTAINS','黑芝麻',0.98,'SRC001','APPROVED','SYNCED'),('PIS0087',19,19,1,'INGREDIENT','ING053','海苔','CONTAINS','海苔',0.99,'SRC001','APPROVED','SYNCED'),('PIS0088',19,19,1,'INGREDIENT','ING032','酵母','CONTAINS','酵母',0.99,'SRC001','APPROVED','SYNCED'),('PIS0089',19,19,1,'INGREDIENT','ING031','海盐','CONTAINS','海盐',0.99,'SRC001','APPROVED','SYNCED'),('PIS0090',19,19,1,'ADDITIVE','ADD009','碳酸氢钠','CONTAINS','碳酸氢钠',0.99,'SRC001','APPROVED','SYNCED'),
('PIS0091',20,20,1,'INGREDIENT','ING007','小麦','CONTAINS','小麦粉',0.99,'SRC001','APPROVED','SYNCED'),('PIS0092',20,20,1,'INGREDIENT','ING054','香菇','CONTAINS','香菇',0.99,'SRC001','APPROVED','SYNCED'),('PIS0093',20,20,1,'INGREDIENT','ING055','杏鲍菇','CONTAINS','杏鲍菇',0.99,'SRC001','APPROVED','SYNCED'),('PIS0094',20,20,1,'INGREDIENT','ING056','酱油粉','CONTAINS','酱油粉',0.96,'SRC001','APPROVED','SYNCED'),('PIS0095',20,20,1,'INGREDIENT','ING057','葱','CONTAINS','葱',0.99,'SRC001','APPROVED','SYNCED'),('PIS0096',20,20,1,'ADDITIVE','ADD010','谷氨酸钠','CONTAINS','谷氨酸钠',0.99,'SRC001','APPROVED','SYNCED'),('PIS0097',20,20,1,'ADDITIVE','ADD011','呈味核苷酸二钠','CONTAINS','呈味核苷酸二钠',0.99,'SRC001','APPROVED','SYNCED')
ON DUPLICATE KEY UPDATE normalized_name=VALUES(normalized_name),audit_status=VALUES(audit_status),updated_at=CURRENT_TIMESTAMP(3);

-- Five nutritional measurements per product; basis and unit are always explicit.
INSERT INTO product_nutrition (product_id,spec_id,nutrient_code,nutrient_name,nutrient_value,unit,basis,basis_quantity,source_code,audit_status)
SELECT p.id,p.id,n.nutrient_code,n.nutrient_name,
  CASE n.nutrient_code
    WHEN 'NUT_ENERGY' THEN ELT(p.id,1510,1920,1920,280,390,1480,185,1050,1480,310,620,1480,190,210,1480,1430,1480,430,1730,1520)
    WHEN 'NUT_PROTEIN' THEN ELT(p.id,11.2,9.5,7.2,3.3,8.5,9.5,0.7,10.1,9.5,1.8,12.8,9.5,4.2,1.1,9.5,8.9,9.5,4.5,9.1,9.8)
    WHEN 'NUT_FAT' THEN ELT(p.id,7.1,6.2,18.4,3.8,6.8,6.2,0.1,7.2,6.2,3.2,4.6,6.2,2.1,1.8,6.2,5.4,6.2,3.2,10.2,12.1)
    WHEN 'NUT_SUGAR' THEN ELT(p.id,4.6,7.8,14.8,4.9,3.9,7.8,8.6,3.2,7.8,5.1,2.1,7.8,0,3.7,7.8,7.2,7.8,8.9,2.8,2.3)
    WHEN 'NUT_SODIUM' THEN ELT(p.id,52,85,320,60,72,85,3,290,85,410,520,85,45,38,85,41,85,66,470,780)
  END AS nutrient_value,
  n.unit,'PER_100G',100,'SRC001','APPROVED'
FROM product p
CROSS JOIN (
  SELECT 'NUT_ENERGY' nutrient_code,'能量' nutrient_name,'kJ' unit UNION ALL
  SELECT 'NUT_PROTEIN','蛋白质','g' UNION ALL SELECT 'NUT_FAT','脂肪','g' UNION ALL
  SELECT 'NUT_SUGAR','糖','g' UNION ALL SELECT 'NUT_SODIUM','钠','mg'
) n
WHERE p.id BETWEEN 1 AND 20
ON DUPLICATE KEY UPDATE nutrient_value=VALUES(nutrient_value),unit=VALUES(unit),basis=VALUES(basis),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO cart (id,cart_code,user_id,status) VALUES (1,'CART0001',1,'ACTIVE'),(2,'CART0002',2,'ACTIVE'),(3,'CART0003',3,'ACTIVE')
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3);
INSERT INTO cart_item (id,cart_id,product_id,spec_id,quantity,selected_flag,added_price) VALUES
(1,1,1,1,1,1,36.90),(2,1,13,13,2,1,46.80),(3,1,15,15,1,0,19.90),(4,2,5,5,1,1,42.00),(5,3,7,7,2,1,32.80)
ON DUPLICATE KEY UPDATE quantity=VALUES(quantity),selected_flag=VALUES(selected_flag),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO favorite (id,user_id,product_id,created_at) VALUES
(1,1,2,'2026-07-10 10:00:00.000'),(2,1,5,'2026-07-11 10:00:00.000'),(3,2,13,'2026-07-12 10:00:00.000'),(4,3,1,'2026-07-13 10:00:00.000'),(5,4,16,'2026-07-14 10:00:00.000')
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO browsing_history (id,user_id,product_id,view_count,last_viewed_at) VALUES
(1,1,9,2,'2026-07-18 09:20:00.000'),(2,1,10,1,'2026-07-18 09:25:00.000'),(3,1,11,3,'2026-07-18 09:30:00.000'),
(4,1,12,1,'2026-07-18 09:35:00.000'),(5,1,13,4,'2026-07-18 09:40:00.000'),(6,1,14,2,'2026-07-18 09:45:00.000')
ON DUPLICATE KEY UPDATE view_count=VALUES(view_count),last_viewed_at=VALUES(last_viewed_at),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO order_info (id,order_no,user_id,merchant_id,order_status,payment_status,receiver_snapshot,goods_amount,discount_amount,shipping_amount,payable_amount,paid_amount,placed_at,paid_at,shipped_at,completed_at,cancelled_at,cancel_reason) VALUES
(1,'ZW202607180031',1,1,'PENDING_SHIPMENT','PAID',JSON_OBJECT('name','林小满','phone','138****8000','address','上海市徐汇区虹桥路718号2栋1206'),88.60,1.90,0,86.70,86.70,'2026-07-18 10:24:00.000','2026-07-18 10:25:00.000',NULL,NULL,NULL,NULL),
(2,'ZW202607160118',2,1,'SHIPPED','PAID',JSON_OBJECT('name','周亦安','phone','138****1002','address','江苏省南京市鼓楼区中山北路66号'),88.80,10.00,0,78.80,78.80,'2026-07-16 16:12:00.000','2026-07-16 16:13:00.000','2026-07-17 09:00:00.000',NULL,NULL,NULL),
(3,'ZW202607140086',1,1,'COMPLETED','PAID',JSON_OBJECT('name','林小满','phone','138****8000','address','上海市徐汇区虹桥路718号2栋1206'),59.70,0,7.10,66.80,66.80,'2026-07-14 09:45:00.000','2026-07-14 09:46:00.000','2026-07-14 15:00:00.000','2026-07-16 10:00:00.000',NULL,NULL),
(4,'ZW202607120055',3,1,'PENDING_PAYMENT','UNPAID',JSON_OBJECT('name','陈子衿','phone','138****1003','address','浙江省杭州市西湖区文三路128号'),59.90,0,0,59.90,0,'2026-07-12 20:03:00.000',NULL,NULL,NULL,NULL,NULL),
(5,'ZW202607080142',4,1,'REFUND_REQUESTED','PAID',JSON_OBJECT('name','梁朵','phone','138****1004','address','广东省深圳市南山区科技园南区18号'),31.80,0,0,31.80,31.80,'2026-07-08 11:30:00.000','2026-07-08 11:31:00.000','2026-07-08 17:00:00.000',NULL,NULL,NULL),
(6,'ZW202607010091',5,1,'CANCELLED','UNPAID',JSON_OBJECT('name','王知秋','phone','138****1005','address','北京市朝阳区演示地址5号'),49.90,0,0,49.90,0,'2026-07-01 15:21:00.000',NULL,NULL,NULL,'2026-07-01 15:40:00.000','用户取消'),
(7,'ZW202606280173',6,1,'COMPLETED','PAID',JSON_OBJECT('name','唐禾','phone','138****1006','address','四川省成都市高新区演示地址6号'),62.30,0,1.10,63.40,63.40,'2026-06-28 18:40:00.000','2026-06-28 18:41:00.000','2026-06-29 09:00:00.000','2026-07-01 12:00:00.000',NULL,NULL),
(8,'ZW202606250064',1,1,'COMPLETED','PAID',JSON_OBJECT('name','林小满','phone','138****8000','address','上海市徐汇区虹桥路718号2栋1206'),46.80,0,0,46.80,46.80,'2026-06-25 08:18:00.000','2026-06-25 08:19:00.000','2026-06-25 14:00:00.000','2026-06-27 11:00:00.000',NULL,NULL)
ON DUPLICATE KEY UPDATE order_status=VALUES(order_status),payment_status=VALUES(payment_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO order_item (id,order_id,order_item_code,product_id,spec_id,product_code_snapshot,product_name_snapshot,spec_code_snapshot,spec_name_snapshot,image_url_snapshot,unit_price,quantity,subtotal_amount,ingredient_version_snapshot) VALUES
(1,1,'OI-0001',1,1,'FP0001','原味低糖燕麦脆','SPEC-FP0001-01','400g/袋','https://images.unsplash.com/photo-1517673400267-0251440c45dc',36.90,1,36.90,1),
(2,1,'OI-0002',2,2,'FP0002','莓果奇亚籽谷物杯','SPEC-FP0002-01','400g/袋','https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea',29.80,1,29.80,1),
(3,1,'OI-0003',19,19,'FP0019','芝麻海苔苏打饼干','SPEC-FP0019-01','400g/袋','https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e',21.90,1,21.90,1),
(4,2,'OI-0004',5,5,'FP0005','希腊式原味酸奶','SPEC-FP0005-01','120g×6杯',NULL,42.00,1,42.00,1),(5,2,'OI-0005',13,13,'FP0013','无糖高蛋白豆乳','SPEC-FP0013-01','250mL×8盒',NULL,46.80,1,46.80,1),
(6,3,'OI-0006',7,7,'FP0007','NFC鲜榨橙汁','SPEC-FP0007-01','300mL×4瓶',NULL,32.80,1,32.80,1),(7,3,'OI-0007',10,10,'FP0010','零添加番茄意面酱','SPEC-FP0010-01','400g/袋',NULL,26.90,1,26.90,1),
(8,4,'OI-0008',4,4,'FP0004','有机全脂鲜牛奶','SPEC-FP0004-01','250mL×10盒',NULL,59.90,1,59.90,1),
(9,5,'OI-0009',11,11,'FP0011','藜麦鸡肉暖食碗','SPEC-FP0011-01','280g/盒',NULL,31.80,1,31.80,1),
(10,6,'OI-0010',6,6,'FP0006','每日原味混合坚果','SPEC-FP0006-01','25g×14袋',NULL,49.90,1,49.90,1),
(11,7,'OI-0011',8,8,'FP0008','全麦核桃软欧包','SPEC-FP0008-01','400g/袋',NULL,22.80,1,22.80,1),(12,7,'OI-0012',16,16,'FP0016','肉桂苹果烤燕麦','SPEC-FP0016-01','400g/袋',NULL,39.50,1,39.50,1),
(13,8,'OI-0013',13,13,'FP0013','无糖高蛋白豆乳','SPEC-FP0013-01','250mL×8盒',NULL,46.80,1,46.80,1)
ON DUPLICATE KEY UPDATE product_name_snapshot=VALUES(product_name_snapshot),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO payment_record (id,payment_no,order_id,payment_channel,payment_status,amount,requested_at,completed_at) VALUES
(1,'PAY0001',1,'MOCK_BALANCE','SUCCESS',86.70,'2026-07-18 10:24:30.000','2026-07-18 10:25:00.000'),
(2,'PAY0002',2,'MOCK_ALIPAY','SUCCESS',78.80,'2026-07-16 16:12:30.000','2026-07-16 16:13:00.000'),
(3,'PAY0003',3,'MOCK_WECHAT','SUCCESS',66.80,'2026-07-14 09:45:30.000','2026-07-14 09:46:00.000'),
(4,'PAY0004',4,'MOCK_BALANCE','PENDING',59.90,'2026-07-12 20:03:10.000',NULL),
(5,'PAY0005',5,'MOCK_ALIPAY','SUCCESS',31.80,'2026-07-08 11:30:20.000','2026-07-08 11:31:00.000'),
(6,'PAY0006',7,'MOCK_WECHAT','SUCCESS',63.40,'2026-06-28 18:40:20.000','2026-06-28 18:41:00.000'),
(7,'PAY0007',8,'MOCK_BALANCE','SUCCESS',46.80,'2026-06-25 08:18:20.000','2026-06-25 08:19:00.000')
ON DUPLICATE KEY UPDATE payment_status=VALUES(payment_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product_review (id,review_code,order_item_id,user_id,product_id,rating,review_text,status,reviewed_at) VALUES
(1,'REV0001',1,1,1,5,'配料解释很清楚，筛选花生风险很方便','PUBLISHED','2026-07-17 10:00:00.000'),
(2,'REV0002',4,2,5,4,'口感清爽，包装信息完整','PUBLISHED','2026-07-17 11:00:00.000'),
(3,'REV0003',8,3,4,5,'图谱能看到别名关系，很安心','PUBLISHED','2026-07-17 12:00:00.000'),
(4,'REV0004',9,4,11,4,'低糖但不会太寡淡','PUBLISHED','2026-07-17 13:00:00.000'),
(5,'REV0005',10,5,6,5,'对比功能比自己看标签快很多','PUBLISHED','2026-07-17 14:00:00.000'),
(6,'REV0006',11,6,8,5,'燕麦颗粒很足','PUBLISHED','2026-07-17 15:00:00.000'),
(7,'REV0007',NULL,7,16,4,'希望增加更多规格','PUBLISHED','2026-07-17 16:00:00.000'),
(8,'REV0008',NULL,1,13,5,'物流快，保质期新鲜','PUBLISHED','2026-07-17 17:00:00.000'),
(9,'REV0009',NULL,2,2,4,'信息来源标注得很明确','PUBLISHED','2026-07-17 18:00:00.000'),
(10,'REV0010',NULL,3,7,5,'愿意继续回购','PUBLISHED','2026-07-17 19:00:00.000')
ON DUPLICATE KEY UPDATE rating=VALUES(rating),review_text=VALUES(review_text),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO product_audit (id,audit_code,product_id,product_version,audit_stage,audit_status,normalized_result,conflict_result,audit_opinion,auditor_user_id,submitted_by,submitted_at,audited_at) VALUES
(1,'RV-0872',1,2,'MANUAL_REVIEW','PENDING',JSON_OBJECT('productName','南瓜籽谷物脆','confidence',0.94),JSON_OBJECT('count',2),'等待人工审核',NULL,8,'2026-07-18 09:50:00.000',NULL),
(2,'RV-0871',13,2,'KNOWLEDGE_REVIEW','TRANSFERRED',JSON_OBJECT('productName','无糖杏仁饮','confidence',0.91),JSON_OBJECT('alias','杏仁饮'),'转知识管理员确认别名',12,8,'2026-07-18 09:34:00.000','2026-07-18 09:40:00.000'),
(3,'RV-0870',11,2,'MANUAL_REVIEW','NEED_MORE_INFO',JSON_OBJECT('productName','番茄牛腩饭'),JSON_OBJECT('nutritionUnit','unknown'),'营养单位需补充',11,8,'2026-07-18 08:30:00.000','2026-07-18 09:00:00.000'),
(4,'RV-0869',3,2,'MANUAL_REVIEW','PENDING',JSON_OBJECT('productName','可可燕麦曲奇'),JSON_OBJECT('allergenNotice','pending'),'核对过敏原提示',NULL,8,'2026-07-18 07:30:00.000',NULL),
(5,'RV-0868',6,2,'MANUAL_REVIEW','APPROVED',JSON_OBJECT('productName','原味腰果酱'),JSON_OBJECT('count',0),'标签与结构化结果一致',11,8,'2026-07-17 09:00:00.000','2026-07-18 09:42:00.000')
ON DUPLICATE KEY UPDATE audit_status=VALUES(audit_status),audit_opinion=VALUES(audit_opinion),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO anomaly_record (id,anomaly_code,anomaly_type,target_type,target_code,title,detail_text,severity,process_status,assignee_user_id,detected_at) VALUES
(1,'EX-1428','UNKNOWN_INGREDIENT','PRODUCT','FP0015','未识别成分','复配谷物粉未展开','HIGH','OPEN',NULL,'2026-07-18 10:10:00.000'),
(2,'EX-1427','NUTRITION_UNIT','PRODUCT','FP0003','营养单位异常','钠单位疑似 mg/份','MEDIUM','PROCESSING',13,'2026-07-18 09:48:00.000'),
(3,'EX-1426','GRAPH_CONFLICT','INGREDIENT','ING001','图谱关系冲突','燕麦与麸质的两个来源结论不一致','HIGH','REVIEWING',12,'2026-07-18 09:00:00.000'),
(4,'EX-1425','MODEL_FAILURE','BATCH','UP-901','模型处理失败','结构化输出校验失败','MEDIUM','RETRIED',13,'2026-07-18 08:00:00.000'),
(5,'EX-1424','INGREDIENT_MISSING','PRODUCT','FP-DEMO-EXTRA','配料缺失','山野莓果棒无原始配料文本','HIGH','NEED_MORE_INFO',8,'2026-07-18 07:00:00.000'),
(6,'EX-1423','ALIAS_UNMAPPED','ADDITIVE','ADD002','别名未映射','E322建议映射为卵磷脂','MEDIUM','PENDING_CONFIRMATION',12,'2026-07-17 16:00:00.000')
ON DUPLICATE KEY UPDATE process_status=VALUES(process_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO ai_conversation (id,conversation_code,user_id,conversation_type,context_summary,status,expires_at) VALUES
(1,'CONV0001',1,'SMART_FILTER','早餐麦片，排除花生，50元内','CLOSED','2026-07-19 10:18:00.000'),
(2,'CONV0002',1,'SMART_FILTER','高蛋白无糖植物奶','CLOSED','2026-07-18 19:42:00.000'),
(3,'CONV0003',2,'SMART_FILTER','低糖饼干，配料简单','CLOSED','2026-07-16 14:20:00.000'),
(4,'CONV0004',3,'SMART_FILTER','无乳糖早餐','CLOSED','2026-07-12 08:03:00.000'),
(5,'CONV0005',4,'SMART_FILTER','低钠速食','CLOSED','2026-07-09 21:16:00.000')
ON DUPLICATE KEY UPDATE context_summary=VALUES(context_summary),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO ai_filter_history (id,filter_code,conversation_id,user_id,raw_query,parsed_conditions,hard_constraints,soft_preferences,pending_confirmations,result_count,execution_mode,parse_status,rule_result_summary,executed_at) VALUES
(1,'FILTER0001',1,1,'不含花生及花生制品、50元以内的早餐麦片',JSON_ARRAY('早餐麦片','排除花生','价格<=50','低糖'),JSON_ARRAY('CAT001','ING002','ING003','ING004','MAX_PRICE_50'),JSON_ARRAY('LOW_SUGAR'),JSON_ARRAY(),8,'AI_GRAPH','SUCCESS',JSON_OBJECT('fullMatch',4,'risk',2,'notMatch',1,'insufficient',1),'2026-07-18 10:18:00.000'),
(2,'FILTER0002',2,1,'高蛋白、无添加糖的植物奶',JSON_ARRAY('植物蛋白','蛋白质>=3g','无添加糖'),JSON_ARRAY('CAT010','NO_ADDED_SUGAR'),JSON_ARRAY('HIGH_PROTEIN'),JSON_ARRAY(),5,'AI_GRAPH','SUCCESS',JSON_OBJECT('resultCount',5),'2026-07-17 19:42:00.000'),
(3,'FILTER0003',3,2,'适合下午茶的低糖饼干，配料简单',JSON_ARRAY('饼干糕点','低糖','配料<=8项'),JSON_ARRAY('CAT002'),JSON_ARRAY('LOW_SUGAR','SIMPLE_INGREDIENTS'),JSON_ARRAY(),12,'AI_GRAPH','SUCCESS',JSON_OBJECT('resultCount',12),'2026-07-15 14:20:00.000'),
(4,'FILTER0004',4,3,'不含乳糖的早餐搭配',JSON_ARRAY('排除乳糖','早餐场景'),JSON_ARRAY('ING014'),JSON_ARRAY('BREAKFAST'),JSON_ARRAY(),16,'AI_GRAPH','SUCCESS',JSON_OBJECT('resultCount',16),'2026-07-11 08:03:00.000'),
(5,'FILTER0005',5,4,'钠低于500mg的速食',JSON_ARRAY('调味速食','钠<=500mg/100g'),JSON_ARRAY('CAT008','SODIUM_MAX_500'),JSON_ARRAY(),JSON_ARRAY(),7,'AI_GRAPH','SUCCESS',JSON_OBJECT('resultCount',7),'2026-07-08 21:16:00.000'),
(6,'FILTER0006',NULL,1,'纯果汁，不要香精和甜味剂',JSON_ARRAY('果汁饮品','100%果汁','排除香精','排除甜味剂'),JSON_ARRAY('CAT005','NO_FLAVOR','NO_SWEETENER'),JSON_ARRAY('PURE_JUICE'),JSON_ARRAY(),6,'BASIC_FORM','DEGRADED',JSON_OBJECT('reason','MODEL_TIMEOUT','resultCount',6),'2026-07-02 12:28:00.000')
ON DUPLICATE KEY UPDATE result_count=VALUES(result_count),parse_status=VALUES(parse_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO ai_model_call_log (id,call_code,conversation_id,filter_history_id,user_id,model_provider,model_name,request_type,prompt_template_version,request_hash,response_status,validation_status,latency_ms,input_tokens,output_tokens,called_at) VALUES
(1,'CALL0001',1,1,1,'QWEN','qwen-mock','INTENT_PARSE','v1.3','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','SUCCESS','PASSED',820,320,110,'2026-07-18 10:18:00.000'),
(2,'CALL0002',2,2,1,'QWEN','qwen-mock','INTENT_PARSE','v1.3','bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb','SUCCESS','PASSED',760,280,96,'2026-07-17 19:42:00.000'),
(3,'CALL0003',3,3,2,'QWEN','qwen-mock','INTENT_PARSE','v1.3','cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc','SUCCESS','PASSED',920,300,105,'2026-07-15 14:20:00.000'),
(4,'CALL0004',4,4,3,'QWEN','qwen-mock','INTENT_PARSE','v1.3','dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd','SUCCESS','PASSED',680,220,88,'2026-07-11 08:03:00.000'),
(5,'CALL0005',5,5,4,'QWEN','qwen-mock','INTENT_PARSE','v1.3','eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee','SUCCESS','PASSED',710,240,91,'2026-07-08 21:16:00.000')
ON DUPLICATE KEY UPDATE response_status=VALUES(response_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO feedback_ticket (id,ticket_code,reporter_user_id,ticket_type,target_type,target_code,feedback_text,status,priority,assignee_user_id) VALUES
(1,'TKT0001',1,'INGREDIENT_CORRECTION','PRODUCT','FP0015','复配谷物粉需要展开具体成分','PROCESSING','HIGH',12),
(2,'TKT0002',2,'FILTER_FEEDBACK','FILTER','FILTER0003','结果解释很清楚','CLOSED','LOW',12),
(3,'TKT0003',4,'AFTER_SALES','ORDER','ZW202607080142','申请退款处理','OPEN','HIGH',11)
ON DUPLICATE KEY UPDATE status=VALUES(status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO audit_log (id,audit_log_code,operator_user_id,operator_name_snapshot,operation_type,object_type,object_code,before_value,after_value,reason,operated_at) VALUES
(1,'AL-5129',11,'顾岚','AUDIT_APPROVED','PRODUCT_AUDIT','RV-0868',JSON_OBJECT('status','PENDING'),JSON_OBJECT('status','APPROVED'),'标签与结构化结果一致','2026-07-18 09:42:00.000'),
(2,'AL-5128',12,'周研','ALIAS_UPDATED','INGREDIENT','ADD002',JSON_OBJECT('alias','UNMAPPED'),JSON_OBJECT('alias','卵磷脂'),'依据GB 2760标准','2026-07-18 09:18:00.000'),
(3,'AL-5127',13,'赵宁','PERMISSION_RESTORED','MERCHANT','MCH0032',JSON_OBJECT('status','FROZEN'),JSON_OBJECT('status','ACTIVE'),'资质补充完成','2026-07-17 17:06:00.000'),
(4,'AL-5126',11,'顾岚','AUDIT_MORE_INFO','PRODUCT_AUDIT','RV-0864',JSON_OBJECT('status','PENDING'),JSON_OBJECT('status','NEED_MORE_INFO'),'原始配料图片不清晰','2026-07-17 15:42:00.000'),
(5,'AL-5125',NULL,'系统','GRAPH_VERSION_PUBLISHED','GRAPH_VERSION','v2.18.0',JSON_OBJECT('version','v2.17.3'),JSON_OBJECT('version','v2.18.0'),'合并12条标准别名','2026-07-16 22:10:00.000'),
(6,'AL-5124',12,'周研','RELATION_UPDATED','GRAPH_RELATION','ING004_TO_ING002',JSON_OBJECT('relation','RELATED_TO'),JSON_OBJECT('relation','DERIVED_FROM'),'关系语义校准','2026-07-16 16:33:00.000')
ON DUPLICATE KEY UPDATE reason=VALUES(reason),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO workflow_task (id,task_code,workflow_type,workflow_instance_code,business_type,business_code,node_code,node_name,task_status,assignee_user_id,candidate_role_code,due_at) VALUES
(1,'WT0001','PRODUCT_AUDIT','RV-0872','PRODUCT','FP0001','MANUAL_REVIEW','人工审核','PENDING',11,'PLATFORM_ADMIN','2026-07-19 09:50:00.000'),
(2,'WT0002','KNOWLEDGE_REVIEW','RV-0871','PRODUCT','FP0013','ALIAS_CONFIRM','别名确认','PROCESSING',12,'KNOWLEDGE_ADMIN','2026-07-19 09:34:00.000'),
(3,'WT0003','ANOMALY','EX-1428','PRODUCT','FP0015','UNKNOWN_TERM','未知词条处理','PENDING',12,'KNOWLEDGE_ADMIN','2026-07-19 10:10:00.000'),
(4,'WT0004','FEEDBACK','TKT0001','FEEDBACK','TKT0001','CORRECTION_REVIEW','纠错复核','PROCESSING',12,'KNOWLEDGE_ADMIN','2026-07-20 10:00:00.000'),
(5,'WT0005','RECHECK','GRAPH-v2.18.0','GRAPH_VERSION','v2.18.0','IMPACT_RECHECK','影响商品重新核验','PENDING',NULL,'PLATFORM_ADMIN','2026-07-21 10:00:00.000')
ON DUPLICATE KEY UPDATE task_status=VALUES(task_status),updated_at=CURRENT_TIMESTAMP(3);

INSERT INTO knowledge_audit (id,knowledge_audit_code,graph_version,entity_type,entity_code,change_type,before_value,after_value,source_code,audit_status,submitted_by,audited_by,audit_opinion,submitted_at,audited_at) VALUES
(1,'KA0001','v2.18.0','INGREDIENT','ING001','RELATION_CHANGE',JSON_OBJECT('riskRelation','RELATED_TO'),JSON_OBJECT('riskRelation','MAY_CROSS_CONTACT'),'SRC003','APPROVED',12,11,'风险语义更准确','2026-07-16 15:00:00.000','2026-07-16 16:00:00.000'),
(2,'KA0002','v2.18.0','ADDITIVE','ADD002','UPDATE',JSON_OBJECT('alias',JSON_ARRAY()),JSON_OBJECT('alias',JSON_ARRAY('E322','卵磷脂')),'SRC002','APPROVED',12,11,'来源充分','2026-07-16 15:10:00.000','2026-07-16 16:10:00.000'),
(3,'KA0003','v2.18.0','INGREDIENT','ING004','RELATION_CHANGE',JSON_OBJECT('relation','RELATED_TO'),JSON_OBJECT('relation','DERIVED_FROM'),'SRC003','APPROVED',12,11,'关系语义校准','2026-07-16 15:20:00.000','2026-07-16 16:20:00.000'),
(4,'KA0004','v2.18.1','INGREDIENT','UNK001','CREATE',NULL,JSON_OBJECT('name','复配谷物粉'),'SRC001','PENDING',12,NULL,NULL,'2026-07-18 10:15:00.000',NULL),
(5,'KA0005','v2.18.1','RELATION','ING001_RISK001','UPDATE',JSON_OBJECT('status','ACTIVE'),JSON_OBJECT('status','REVIEWING'),'SRC005','PENDING',12,NULL,'等待来源复核','2026-07-18 10:20:00.000',NULL)
ON DUPLICATE KEY UPDATE audit_status=VALUES(audit_status),updated_at=CURRENT_TIMESTAMP(3);

COMMIT;
