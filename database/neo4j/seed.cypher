// FoodPlatform Neo4j 5.x demonstration graph.
// Run after constraints.cypher. All identities are stable business keys shared with MySQL.

UNWIND [
  {code:'BR001',name:'谷本日记'},{code:'BR002',name:'欧扎克'},{code:'BR003',name:'每日盒子'},
  {code:'BR004',name:'牧场清晨'},{code:'BR005',name:'北海乳业'},{code:'BR006',name:'坚果森林'},
  {code:'BR007',name:'橙意满满'},{code:'BR008',name:'麦香工房'},{code:'BR009',name:'可可宇宙'},
  {code:'BR010',name:'味原纪'},{code:'BR011',name:'简食社'},{code:'BR012',name:'植选研究所'},
  {code:'BR013',name:'山野集'},{code:'BR014',name:'轻负担'},{code:'BR015',name:'禾谷里'}
] AS row MERGE (n:Brand {brand_code:row.code}) SET n.name=row.name,n.status='ACTIVE',n.updated_at=datetime();

UNWIND [
  {code:'CAT001',name:'早餐麦片'},{code:'CAT002',name:'饼干糕点'},{code:'CAT003',name:'乳品酸奶'},
  {code:'CAT004',name:'坚果炒货'},{code:'CAT005',name:'果汁饮品'},{code:'CAT006',name:'面包烘焙'},
  {code:'CAT007',name:'巧克力'},{code:'CAT008',name:'调味速食'},{code:'CAT009',name:'谷物能量棒'},
  {code:'CAT010',name:'植物蛋白'}
] AS row MERGE (n:Category {category_code:row.code}) SET n.name=row.name,n.status='ACTIVE',n.updated_at=datetime();

UNWIND [
 {code:'ING001',name:'燕麦',type:'GRAIN'},{code:'ING002',name:'花生',type:'NUT'},
 {code:'ING003',name:'花生粉',type:'NUT'},{code:'ING004',name:'花生酱',type:'NUT'},
 {code:'ING005',name:'牛奶',type:'DAIRY'},{code:'ING006',name:'大豆',type:'LEGUME'},
 {code:'ING007',name:'小麦',type:'GRAIN'},{code:'ING008',name:'鸡蛋',type:'ANIMAL'},
 {code:'ING009',name:'芝麻',type:'SEED'},{code:'ING010',name:'杏仁',type:'NUT'},
 {code:'ING011',name:'腰果',type:'NUT'},{code:'ING012',name:'核桃',type:'NUT'},
 {code:'ING013',name:'榛子',type:'NUT'},{code:'ING014',name:'乳糖',type:'CARBOHYDRATE'},
 {code:'ING015',name:'麸质',type:'PROTEIN'},{code:'ING016',name:'白砂糖',type:'SWEETENER'},
 {code:'ING017',name:'赤藓糖醇',type:'SWEETENER'},{code:'ING018',name:'奇亚籽',type:'SEED'},
 {code:'ING019',name:'藜麦',type:'GRAIN'},{code:'ING020',name:'南瓜籽',type:'SEED'},
 {code:'ING021',name:'葵花籽',type:'SEED'},{code:'ING022',name:'可可液块',type:'COCOA'},
 {code:'ING023',name:'可可脂',type:'FAT'},{code:'ING024',name:'番茄',type:'VEGETABLE'},
 {code:'ING025',name:'洋葱',type:'VEGETABLE'},{code:'ING026',name:'橄榄油',type:'FAT'},
 {code:'ING027',name:'鸡胸肉',type:'ANIMAL'},{code:'ING028',name:'草莓',type:'FRUIT'},
 {code:'ING029',name:'蓝莓',type:'FRUIT'},{code:'ING030',name:'菊粉',type:'FIBER'},
 {code:'ING031',name:'海盐',type:'MINERAL'},{code:'ING032',name:'酵母',type:'MICROORGANISM'},
 {code:'ING033',name:'苹果',type:'FRUIT'},{code:'ING034',name:'肉桂',type:'SPICE'},
 {code:'ING035',name:'罗勒',type:'HERB'},{code:'ING036',name:'玉米',type:'GRAIN'},
 {code:'ING037',name:'椰子片',type:'FRUIT'},{code:'ING038',name:'黄油',type:'DAIRY'},
 {code:'ING039',name:'嗜热链球菌',type:'MICROORGANISM'},{code:'ING040',name:'保加利亚乳杆菌',type:'MICROORGANISM'},
 {code:'ING041',name:'蔓越莓',type:'FRUIT'},{code:'ING042',name:'橙汁',type:'FRUIT'},
 {code:'ING043',name:'麦芽糖浆',type:'SWEETENER'},{code:'ING044',name:'水',type:'OTHER'},
 {code:'ING045',name:'菜籽油',type:'FAT'},{code:'ING046',name:'小米',type:'GRAIN'},
 {code:'ING047',name:'糯米',type:'GRAIN'},{code:'ING048',name:'桂花',type:'HERB'},
 {code:'ING049',name:'麦芽糖',type:'SWEETENER'},{code:'ING050',name:'枫糖浆',type:'SWEETENER'},
 {code:'ING051',name:'植物油',type:'FAT'},{code:'ING052',name:'乳酸菌',type:'MICROORGANISM'},
 {code:'ING053',name:'海苔',type:'ALGAE'},{code:'ING054',name:'香菇',type:'FUNGUS'},
 {code:'ING055',name:'杏鲍菇',type:'FUNGUS'},{code:'ING056',name:'酱油粉',type:'CONDIMENT'},
 {code:'ING057',name:'葱',type:'VEGETABLE'},{code:'ING058',name:'坚果',type:'NUT'},
 {code:'ING059',name:'胡萝卜',type:'VEGETABLE'},{code:'ING060',name:'西兰花',type:'VEGETABLE'},
 {code:'ING061',name:'燕麦片',type:'ALIAS'},{code:'ING062',name:'落花生',type:'ALIAS'},
 {code:'ING063',name:'生牛乳',type:'ALIAS'},{code:'ING064',name:'小麦粉',type:'ALIAS'}
] AS row MERGE (n:Ingredient {ingredient_code:row.code}) SET n.name=row.name,n.ingredient_type=row.type,n.audit_status='APPROVED',n.updated_at=datetime();

UNWIND [
 {code:'ADD001',name:'磷脂',function:'乳化剂'},{code:'ADD002',name:'大豆磷脂',function:'乳化剂'},
 {code:'ADD003',name:'果胶',function:'增稠剂'},{code:'ADD004',name:'抗坏血酸',function:'抗氧化剂'},
 {code:'ADD005',name:'乳酸钠',function:'保鲜剂'},{code:'ADD006',name:'碳酸钙',function:'营养强化剂'},
 {code:'ADD007',name:'维生素D',function:'营养强化剂'},{code:'ADD008',name:'磷酸氢二钾',function:'稳定剂'},
 {code:'ADD009',name:'碳酸氢钠',function:'膨松剂'},{code:'ADD010',name:'谷氨酸钠',function:'增味剂'},
 {code:'ADD011',name:'呈味核苷酸二钠',function:'增味剂'}
] AS row MERGE (n:Additive {additive_code:row.code}) SET n.name=row.name,n.function=row.function,n.audit_status='APPROVED',n.updated_at=datetime();

UNWIND [
 {code:'RISK001',name:'花生及其制品',level:'HIGH'},{code:'RISK002',name:'乳及乳制品',level:'HIGH'},
 {code:'RISK003',name:'大豆及其制品',level:'MEDIUM'},{code:'RISK004',name:'含麸质谷物',level:'HIGH'},
 {code:'RISK005',name:'蛋及蛋制品',level:'HIGH'},{code:'RISK006',name:'芝麻及其制品',level:'MEDIUM'},
 {code:'RISK007',name:'坚果及其制品',level:'HIGH'},{code:'RISK008',name:'高糖',level:'MEDIUM'},
 {code:'RISK009',name:'高钠',level:'MEDIUM'},{code:'RISK010',name:'含食品添加剂',level:'LOW'},
 {code:'RISK011',name:'信息不完整',level:'MEDIUM'},{code:'RISK012',name:'可能交叉污染',level:'MEDIUM'}
] AS row MERGE (n:RiskTag {risk_tag_code:row.code}) SET n.name=row.name,n.risk_level=row.level,n.audit_status='APPROVED',n.updated_at=datetime();

UNWIND [
 {code:'NUT_ENERGY',name:'能量',unit:'kJ'},{code:'NUT_PROTEIN',name:'蛋白质',unit:'g'},
 {code:'NUT_FAT',name:'脂肪',unit:'g'},{code:'NUT_CARBS',name:'碳水化合物',unit:'g'},
 {code:'NUT_SUGAR',name:'糖',unit:'g'},{code:'NUT_SODIUM',name:'钠',unit:'mg'},
 {code:'NUT_FIBER',name:'膳食纤维',unit:'g'},{code:'NUT_CALCIUM',name:'钙',unit:'mg'},
 {code:'NUT_VITAMIN_D',name:'维生素D',unit:'µg'},{code:'NUT_SATURATED_FAT',name:'饱和脂肪',unit:'g'}
] AS row MERGE (n:Nutrient {nutrient_code:row.code}) SET n.name=row.name,n.default_unit=row.unit,n.updated_at=datetime();

UNWIND [
 {code:'SRC001',name:'商品包装标签',type:'LABEL'},{code:'SRC002',name:'商家提交',type:'MERCHANT'},
 {code:'SRC003',name:'平台人工复核',type:'MANUAL_REVIEW'},{code:'SRC004',name:'国家标准',type:'STANDARD'},
 {code:'SRC005',name:'用户纠错',type:'USER_FEEDBACK'}
] AS row MERGE (n:DataSource {source_code:row.code}) SET n.name=row.name,n.source_type=row.type,n.updated_at=datetime();

UNWIND [
 {code:'FP0001',name:'原味低糖燕麦脆',brand:'BR001',category:'CAT001',status:'FULL_MATCH'},
 {code:'FP0002',name:'莓果奇亚籽谷物杯',brand:'BR002',category:'CAT001',status:'RISK'},
 {code:'FP0003',name:'海盐燕麦曲奇',brand:'BR014',category:'CAT002',status:'NOT_MATCH'},
 {code:'FP0004',name:'有机全脂鲜牛奶',brand:'BR004',category:'CAT003',status:'FULL_MATCH'},
 {code:'FP0005',name:'希腊式原味酸奶',brand:'BR005',category:'CAT003',status:'FULL_MATCH'},
 {code:'FP0006',name:'每日原味混合坚果',brand:'BR006',category:'CAT004',status:'RISK'},
 {code:'FP0007',name:'NFC鲜榨橙汁',brand:'BR007',category:'CAT005',status:'FULL_MATCH'},
 {code:'FP0008',name:'全麦核桃软欧包',brand:'BR008',category:'CAT006',status:'FULL_MATCH'},
 {code:'FP0009',name:'72%黑巧克力薄片',brand:'BR009',category:'CAT007',status:'RISK'},
 {code:'FP0010',name:'零添加番茄意面酱',brand:'BR010',category:'CAT008',status:'FULL_MATCH'},
 {code:'FP0011',name:'藜麦鸡肉暖食碗',brand:'BR011',category:'CAT008',status:'FULL_MATCH'},
 {code:'FP0012',name:'海盐黑巧谷物棒',brand:'BR015',category:'CAT009',status:'NOT_MATCH'},
 {code:'FP0013',name:'无糖高蛋白豆乳',brand:'BR012',category:'CAT010',status:'FULL_MATCH'},
 {code:'FP0014',name:'燕麦植物奶',brand:'BR012',category:'CAT010',status:'FULL_MATCH'},
 {code:'FP0015',name:'桂花小米酥',brand:'BR013',category:'CAT002',status:'INFORMATION_INSUFFICIENT'},
 {code:'FP0016',name:'肉桂苹果烤燕麦',brand:'BR001',category:'CAT001',status:'FULL_MATCH'},
 {code:'FP0017',name:'原味花生酱夹心饼',brand:'BR003',category:'CAT002',status:'NOT_MATCH'},
 {code:'FP0018',name:'草莓谷物轻酸奶',brand:'BR005',category:'CAT003',status:'FULL_MATCH'},
 {code:'FP0019',name:'芝麻海苔苏打饼干',brand:'BR014',category:'CAT002',status:'FULL_MATCH'},
 {code:'FP0020',name:'低钠菌菇汤面',brand:'BR011',category:'CAT008',status:'FULL_MATCH'}
] AS row
MERGE (p:FoodProduct {product_code:row.code})
SET p.name=row.name,p.match_status=row.status,p.audit_status='APPROVED',p.graph_version='v1.0',p.updated_at=datetime()
WITH p,row MATCH (b:Brand {brand_code:row.brand}) MERGE (p)-[:FOOD_PRODUCT_BELONGS_TO_BRAND]->(b)
WITH p,row MATCH (c:Category {category_code:row.category}) MERGE (p)-[:FOOD_PRODUCT_BELONGS_TO_CATEGORY]->(c);

UNWIND [
 {p:'FP0001',i:['ING001','ING019','ING020','ING037','ING030']},
 {p:'FP0002',i:['ING001','ING028','ING029','ING018']},
 {p:'FP0003',i:['ING007','ING001','ING038','ING031','ING016']},
 {p:'FP0004',i:['ING005']},{p:'FP0005',i:['ING005','ING039','ING040']},
 {p:'FP0006',i:['ING010','ING011','ING012','ING013','ING041']},{p:'FP0007',i:['ING042']},
 {p:'FP0008',i:['ING007','ING012','ING032','ING031']},{p:'FP0009',i:['ING022','ING023','ING017','ING016']},
 {p:'FP0010',i:['ING024','ING025','ING026','ING035','ING031']},{p:'FP0011',i:['ING019','ING027','ING036','ING059','ING060']},
 {p:'FP0012',i:['ING001','ING022','ING043','ING010','ING031']},{p:'FP0013',i:['ING044','ING006']},
 {p:'FP0014',i:['ING044','ING001','ING045','ING031']},{p:'FP0015',i:['ING046','ING047','ING048','ING049']},
 {p:'FP0016',i:['ING001','ING033','ING034','ING021','ING050']},{p:'FP0017',i:['ING007','ING004','ING016','ING051']},
 {p:'FP0018',i:['ING005','ING028','ING001','ING052']},{p:'FP0019',i:['ING007','ING009','ING053','ING032','ING031']},
 {p:'FP0020',i:['ING007','ING054','ING055','ING056','ING057']}
] AS row MATCH (p:FoodProduct {product_code:row.p}) UNWIND row.i AS code
MATCH (i:Ingredient {ingredient_code:code})
MERGE (p)-[r:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(i)
SET r.source_code='SRC001',r.audit_status='APPROVED',r.confidence=0.98,r.version='v1.0';

UNWIND [
 {p:'FP0002',i:['ING002']},
 {p:'FP0006',i:['ING002']},
 {p:'FP0009',i:['ING005','ING058']}
] AS row MATCH (p:FoodProduct {product_code:row.p}) UNWIND row.i AS code
MATCH (i:Ingredient {ingredient_code:code})
MERGE (p)-[r:FOOD_PRODUCT_MAY_CONTAIN]->(i)
SET r.source_code='SRC001',r.audit_status='APPROVED',r.confidence=0.90,r.version='v1.0';

UNWIND [
 {p:'FP0002',a:['ADD001']},{p:'FP0008',a:['ADD004']},
 {p:'FP0009',a:['ADD002']},{p:'FP0011',a:['ADD005']},
 {p:'FP0012',a:['ADD002']},{p:'FP0013',a:['ADD006','ADD007']},
 {p:'FP0014',a:['ADD008']},{p:'FP0018',a:['ADD003']},
 {p:'FP0019',a:['ADD009']},{p:'FP0020',a:['ADD010','ADD011']}
] AS row MATCH (p:FoodProduct {product_code:row.p}) UNWIND row.a AS code
MATCH (a:Additive {additive_code:code}) MERGE (p)-[r:FOOD_PRODUCT_HAS_ADDITIVE]->(a)
SET r.source_code='SRC001',r.audit_status='APPROVED',r.version='v1.0';

UNWIND [
 {p:'FP0001',v:[1510,11.2,7.1,4.6,52]},{p:'FP0002',v:[1920,9.5,6.2,7.8,85]},
 {p:'FP0003',v:[1920,7.2,18.4,14.8,320]},{p:'FP0004',v:[280,3.3,3.8,4.9,60]},
 {p:'FP0005',v:[390,8.5,6.8,3.9,72]},{p:'FP0006',v:[1480,9.5,6.2,7.8,85]},
 {p:'FP0007',v:[185,0.7,0.1,8.6,3]},{p:'FP0008',v:[1050,10.1,7.2,3.2,290]},
 {p:'FP0009',v:[1480,9.5,6.2,7.8,85]},{p:'FP0010',v:[310,1.8,3.2,5.1,410]},
 {p:'FP0011',v:[620,12.8,4.6,2.1,520]},{p:'FP0012',v:[1480,9.5,6.2,7.8,85]},
 {p:'FP0013',v:[190,4.2,2.1,0,45]},{p:'FP0014',v:[210,1.1,1.8,3.7,38]},
 {p:'FP0015',v:[1480,9.5,6.2,7.8,85]},{p:'FP0016',v:[1430,8.9,5.4,7.2,41]},
 {p:'FP0017',v:[1480,9.5,6.2,7.8,85]},{p:'FP0018',v:[430,4.5,3.2,8.9,66]},
 {p:'FP0019',v:[1730,9.1,10.2,2.8,470]},{p:'FP0020',v:[1520,9.8,12.1,2.3,780]}
] AS row MATCH (p:FoodProduct {product_code:row.p})
WITH p,row,['NUT_ENERGY','NUT_PROTEIN','NUT_FAT','NUT_SUGAR','NUT_SODIUM'] AS codes
UNWIND range(0,4) AS idx MATCH (n:Nutrient {nutrient_code:codes[idx]})
MERGE (p)-[r:FOOD_PRODUCT_HAS_NUTRIENT]->(n)
SET r.value=row.v[idx],r.unit=CASE idx WHEN 0 THEN 'kJ' WHEN 4 THEN 'mg' ELSE 'g' END,r.basis='PER_100G',r.source_code='SRC001',r.audit_status='APPROVED';

UNWIND [
 {alias:'ING061',canonical:'ING001'},{alias:'ING062',canonical:'ING002'},
 {alias:'ING063',canonical:'ING005'},{alias:'ING064',canonical:'ING007'}
] AS row MATCH (a:Ingredient {ingredient_code:row.alias}),(c:Ingredient {ingredient_code:row.canonical})
MERGE (a)-[r:INGREDIENT_ALIAS_OF]->(c) SET r.audit_status='APPROVED',r.source_code='SRC003';

UNWIND [
 {child:'ING003',parent:'ING002'},{child:'ING004',parent:'ING002'},{child:'ING014',parent:'ING005'},
 {child:'ING015',parent:'ING007'},{child:'ING043',parent:'ING007'},{child:'ING049',parent:'ING043'}
] AS row MATCH (c:Ingredient {ingredient_code:row.child}),(p:Ingredient {ingredient_code:row.parent})
MERGE (c)-[r:INGREDIENT_DERIVED_FROM]->(p) SET r.audit_status='APPROVED',r.source_code='SRC003';

UNWIND [
 {i:'ING002',r:'RISK001'},{i:'ING003',r:'RISK001'},{i:'ING004',r:'RISK001'},
 {i:'ING005',r:'RISK002'},{i:'ING014',r:'RISK002'},{i:'ING006',r:'RISK003'},
 {i:'ING007',r:'RISK004'},{i:'ING015',r:'RISK004'},{i:'ING008',r:'RISK005'},
 {i:'ING009',r:'RISK006'},{i:'ING010',r:'RISK007'},{i:'ING011',r:'RISK007'},
 {i:'ING012',r:'RISK007'},{i:'ING013',r:'RISK007'},{i:'ING058',r:'RISK007'},
 {i:'ING016',r:'RISK008'},{i:'ING031',r:'RISK009'}
] AS row MATCH (i:Ingredient {ingredient_code:row.i}),(tag:RiskTag {risk_tag_code:row.r})
MERGE (i)-[rel:INGREDIENT_HAS_RISK]->(tag) SET rel.audit_status='APPROVED',rel.source_code='SRC004';

UNWIND [
 {a:'ING002',b:'ING021'},{a:'ING005',b:'ING006'},{a:'ING016',b:'ING017'},
 {a:'ING007',b:'ING019'},{a:'ING038',b:'ING026'},{a:'ING010',b:'ING020'}
] AS row MATCH (a:Ingredient {ingredient_code:row.a}),(b:Ingredient {ingredient_code:row.b})
MERGE (a)-[r:INGREDIENT_CAN_SUBSTITUTE]->(b) SET r.note='配方替代建议，需结合具体工艺确认',r.audit_status='APPROVED',r.source_code='SRC003';

MATCH (source:DataSource {source_code:'SRC001'}) MATCH (p:FoodProduct)
MERGE (p)-[r:ENTITY_FROM_SOURCE]->(source) SET r.observed_at=datetime(),r.audit_status='APPROVED';
MATCH (source:DataSource {source_code:'SRC004'}) MATCH (i:Ingredient)
MERGE (i)-[r:ENTITY_FROM_SOURCE]->(source) SET r.observed_at=datetime(),r.audit_status='APPROVED';
MATCH (source:DataSource {source_code:'SRC004'}) MATCH (a:Additive)
MERGE (a)-[r:ENTITY_FROM_SOURCE]->(source) SET r.observed_at=datetime(),r.audit_status='APPROVED';
