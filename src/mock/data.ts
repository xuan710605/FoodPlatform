import type { GraphEdge, GraphNode, Order, Product } from '../types'

const img = (id: string) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=900&q=82`

export const categories = [
  { name: '早餐麦片', icon: '🥣', count: 28 }, { name: '饼干糕点', icon: '🍪', count: 46 },
  { name: '乳品酸奶', icon: '🥛', count: 35 }, { name: '坚果果干', icon: '🥜', count: 41 },
  { name: '果汁饮品', icon: '🍊', count: 32 }, { name: '面包烘焙', icon: '🍞', count: 39 },
  { name: '巧克力', icon: '🍫', count: 24 }, { name: '调味速食', icon: '🍜', count: 51 },
  { name: '谷物能量棒', icon: '🌾', count: 22 }, { name: '植物蛋白', icon: '🌱', count: 30 },
]

export const brands = ['谷本日记', '欧扎克', '每日盒子', '牧场清晨', '北海乳业', '坚果森林', '橙意满满', '麦香工房', '可可宇宙', '味原纪', '简食社', '植选研究所', '山野集', '轻负担', '禾谷里']

const base = {
  gallery: [], rating: 4.8, sales: 1200, stock: 85, spec: '400g/袋', additives: [] as string[], mayContain: [] as string[], unknown: [] as string[],
  nutrition: { energy: 1480, protein: 9.5, fat: 6.2, sugar: 7.8, sodium: 85 },
  status: '完全匹配' as const, reason: '不含已排除成分，糖含量较低，配料信息完整', evidence: '商品标签未检出花生、花生粉或花生酱', source: '商品包装标签 · 商家提交 · 平台人工复核', reviewStatus: '已通过' as const,
  merchant: '知味优选旗舰店', updatedAt: '2026-07-16',
}

export const products: Product[] = [
  { ...base, id: 1, name: '原味低糖燕麦脆', brand: '谷本日记', category: '早餐麦片', price: 36.9, originalPrice: 42.9, image: img('photo-1517673400267-0251440c45dc'), ingredients: ['全粒燕麦', '藜麦', '南瓜籽', '椰子片', '菊粉'], nutrition: { energy: 1510, protein: 11.2, fat: 7.1, sugar: 4.6, sodium: 52 } },
  { ...base, id: 2, name: '莓果奇亚籽谷物杯', brand: '欧扎克', category: '早餐麦片', price: 29.8, image: img('photo-1490474418585-ba9bad8fd0ea'), ingredients: ['燕麦片', '草莓干', '蓝莓干', '奇亚籽', '酸奶块'], additives: ['磷脂'], mayContain: ['花生'], status: '存在风险', reason: '主体配料未见花生，但标签提示同线生产可能含有花生', evidence: '包装过敏原提示：“本生产线亦处理花生制品”' },
  { ...base, id: 3, name: '海盐燕麦曲奇', brand: '轻负担', category: '饼干糕点', price: 24.9, image: img('photo-1558961363-fa8fdf82db35'), ingredients: ['小麦粉', '燕麦', '黄油', '海盐', '白砂糖'], nutrition: { energy: 1920, protein: 7.2, fat: 18.4, sugar: 14.8, sodium: 320 }, status: '不匹配', reason: '糖含量高于当前偏好上限', evidence: '营养标签：糖 14.8g/100g' },
  { ...base, id: 4, name: '有机全脂鲜牛奶', brand: '牧场清晨', category: '乳品酸奶', price: 59.9, spec: '250mL×10盒', image: img('photo-1550583724-b2692b85b150'), ingredients: ['生牛乳'], nutrition: { energy: 280, protein: 3.3, fat: 3.8, sugar: 4.9, sodium: 60 }, reason: '单一配料，无食品添加剂', evidence: '原始配料表仅含“生牛乳”' },
  { ...base, id: 5, name: '希腊式原味酸奶', brand: '北海乳业', category: '乳品酸奶', price: 42, spec: '120g×6杯', image: img('photo-1571212515416-fca77afa8caa'), ingredients: ['生牛乳', '嗜热链球菌', '保加利亚乳杆菌'], nutrition: { energy: 390, protein: 8.5, fat: 6.8, sugar: 3.9, sodium: 72 } },
  { ...base, id: 6, name: '每日原味混合坚果', brand: '坚果森林', category: '坚果果干', price: 49.9, spec: '25g×14袋', image: img('photo-1599599810694-b5b37304c041'), ingredients: ['巴旦木', '腰果', '核桃', '榛子', '蔓越莓干'], mayContain: ['花生'], status: '存在风险', reason: '含多种树坚果，且存在花生交叉接触风险', evidence: '商品标签过敏原信息' },
  { ...base, id: 7, name: 'NFC鲜榨橙汁', brand: '橙意满满', category: '果汁饮品', price: 32.8, spec: '300mL×4瓶', image: img('photo-1621506289937-a8e4df240d0b'), ingredients: ['橙汁'], nutrition: { energy: 185, protein: 0.7, fat: 0.1, sugar: 8.6, sodium: 3 } },
  { ...base, id: 8, name: '全麦核桃软欧包', brand: '麦香工房', category: '面包烘焙', price: 22.8, image: img('photo-1509440159596-0249088772ff'), ingredients: ['全麦粉', '小麦粉', '核桃', '酵母', '海盐'], additives: ['抗坏血酸'], nutrition: { energy: 1050, protein: 10.1, fat: 7.2, sugar: 3.2, sodium: 290 } },
  { ...base, id: 9, name: '72%黑巧克力薄片', brand: '可可宇宙', category: '巧克力', price: 39.8, spec: '100g/盒', image: img('photo-1575377427642-087cf684f29d'), ingredients: ['可可液块', '可可脂', '赤藓糖醇', '白砂糖'], additives: ['大豆磷脂'], mayContain: ['牛奶', '坚果'], status: '存在风险', reason: '可能含牛奶与坚果，需结合个人排除条件确认', evidence: '包装“可能含有”区域' },
  { ...base, id: 10, name: '零添加番茄意面酱', brand: '味原纪', category: '调味速食', price: 26.9, image: img('photo-1472476443507-c7a5948772fc'), ingredients: ['番茄', '洋葱', '橄榄油', '罗勒', '海盐'], nutrition: { energy: 310, protein: 1.8, fat: 3.2, sugar: 5.1, sodium: 410 } },
  { ...base, id: 11, name: '藜麦鸡肉暖食碗', brand: '简食社', category: '调味速食', price: 31.8, spec: '280g/盒', image: img('photo-1547592180-85f173990554'), ingredients: ['藜麦', '鸡胸肉', '玉米', '胡萝卜', '西兰花'], additives: ['乳酸钠'], nutrition: { energy: 620, protein: 12.8, fat: 4.6, sugar: 2.1, sodium: 520 } },
  { ...base, id: 12, name: '海盐黑巧谷物棒', brand: '禾谷里', category: '谷物能量棒', price: 28.5, spec: '30g×6条', image: img('photo-1571748982800-fa51082c2224'), ingredients: ['燕麦', '黑巧克力', '麦芽糖浆', '杏仁', '海盐'], additives: ['大豆磷脂'], status: '不匹配', reason: '含杏仁且糖含量高于偏好', evidence: '配料表与营养标签双重命中' },
  { ...base, id: 13, name: '无糖高蛋白豆乳', brand: '植选研究所', category: '植物蛋白', price: 46.8, spec: '250mL×8盒', image: img('photo-1556881286-fc6915169721'), ingredients: ['水', '非转基因大豆'], additives: ['碳酸钙', '维生素D'], nutrition: { energy: 190, protein: 4.2, fat: 2.1, sugar: 0, sodium: 45 } },
  { ...base, id: 14, name: '燕麦植物奶', brand: '植选研究所', category: '植物蛋白', price: 34.9, spec: '1L/盒', image: img('photo-1600788907416-456578634209'), ingredients: ['水', '燕麦', '菜籽油', '海盐'], additives: ['磷酸氢二钾'], nutrition: { energy: 210, protein: 1.1, fat: 1.8, sugar: 3.7, sodium: 38 } },
  { ...base, id: 15, name: '桂花小米酥', brand: '山野集', category: '饼干糕点', price: 19.9, image: img('photo-1587241321921-91a834d6d191'), ingredients: ['小米', '糯米', '桂花', '麦芽糖'], unknown: ['复配谷物粉'], status: '信息不足', reason: '“复配谷物粉”缺少展开成分，无法判定全部来源', evidence: '原始标签未披露复配配料构成' },
  { ...base, id: 16, name: '肉桂苹果烤燕麦', brand: '谷本日记', category: '早餐麦片', price: 39.5, image: img('photo-1517093157656-b9eccef91cb1'), ingredients: ['全粒燕麦', '苹果干', '肉桂', '葵花籽', '枫糖浆'], nutrition: { energy: 1430, protein: 8.9, fat: 5.4, sugar: 7.2, sodium: 41 } },
  { ...base, id: 17, name: '原味花生酱夹心饼', brand: '每日盒子', category: '饼干糕点', price: 16.8, image: img('photo-1559622214-f8a9850965bb'), ingredients: ['小麦粉', '花生酱', '白砂糖', '植物油'], status: '不匹配', reason: '明确含有用户排除的花生酱', evidence: '原始配料表第2项：花生酱' },
  { ...base, id: 18, name: '草莓谷物轻酸奶', brand: '北海乳业', category: '乳品酸奶', price: 35.8, spec: '180g×4杯', image: img('photo-1563636619-e9143da7973b'), ingredients: ['生牛乳', '草莓果酱', '燕麦脆', '乳酸菌'], additives: ['果胶'], nutrition: { energy: 430, protein: 4.5, fat: 3.2, sugar: 8.9, sodium: 66 } },
  { ...base, id: 19, name: '芝麻海苔苏打饼干', brand: '轻负担', category: '饼干糕点', price: 21.9, image: img('photo-1590080875515-8a3a8dc5735e'), ingredients: ['小麦粉', '黑芝麻', '海苔', '酵母', '海盐'], additives: ['碳酸氢钠'], nutrition: { energy: 1730, protein: 9.1, fat: 10.2, sugar: 2.8, sodium: 470 } },
  { ...base, id: 20, name: '低钠菌菇汤面', brand: '简食社', category: '调味速食', price: 18.5, spec: '92g/杯', image: img('photo-1569718212165-3a8278d5f624'), ingredients: ['小麦粉', '香菇', '杏鲍菇', '酱油粉', '葱'], additives: ['谷氨酸钠', '呈味核苷酸二钠'], nutrition: { energy: 1520, protein: 9.8, fat: 12.1, sugar: 2.3, sodium: 780 } },
]

export const ingredients = ['燕麦','花生','花生粉','花生酱','牛奶','大豆','小麦','鸡蛋','芝麻','杏仁','腰果','核桃','榛子','乳糖','麸质','白砂糖','赤藓糖醇','奇亚籽','藜麦','南瓜籽','葵花籽','可可液块','可可脂','番茄','洋葱','橄榄油','鸡胸肉','草莓','蓝莓','菊粉','海盐','酵母','苹果','肉桂','罗勒','玉米']
export const additives = ['磷脂','大豆磷脂','果胶','抗坏血酸','乳酸钠','碳酸钙','维生素D','磷酸氢二钾','碳酸氢钠','谷氨酸钠','呈味核苷酸二钠']
export const riskTags = ['花生过敏原','乳制品','大豆','含麸质谷物','坚果','鸡蛋','芝麻','高糖','高钠','信息缺失','交叉接触风险','未识别成分']

export const orders: Order[] = [
  { id:'ZW202607180031',date:'2026-07-18 10:24',status:'待发货',amount:86.7,productIds:[1,2,19],buyer:'林小满' },
  { id:'ZW202607160118',date:'2026-07-16 16:12',status:'待收货',amount:78.8,productIds:[5,13],buyer:'周亦安' },
  { id:'ZW202607140086',date:'2026-07-14 09:45',status:'已完成',amount:66.8,productIds:[7,10],buyer:'林小满' },
  { id:'ZW202607120055',date:'2026-07-12 20:03',status:'待付款',amount:59.9,productIds:[4],buyer:'陈子衿' },
  { id:'ZW202607080142',date:'2026-07-08 11:30',status:'退款申请',amount:31.8,productIds:[11],buyer:'梁朵' },
  { id:'ZW202607010091',date:'2026-07-01 15:21',status:'已取消',amount:49.9,productIds:[6],buyer:'王知秋' },
  { id:'ZW202606280173',date:'2026-06-28 18:40',status:'已完成',amount:63.4,productIds:[8,16],buyer:'唐禾' },
  { id:'ZW202606250064',date:'2026-06-25 08:18',status:'已完成',amount:46.8,productIds:[13],buyer:'林小满' },
]

export const reviews = [
  ['林小满',5,'配料解释很清楚，筛选花生风险很方便'],['周亦安',4,'口感清爽，包装信息完整'],['陈子衿',5,'图谱能看到别名关系，很安心'],['梁朵',4,'低糖但不会太寡淡'],['王知秋',5,'对比功能比自己看标签快很多'],['唐禾',5,'燕麦颗粒很足'],['许望舒',4,'希望增加更多规格'],['沈晴',5,'物流快，保质期新鲜'],['乔木',4,'信息来源标注得很明确'],['苏橙',5,'愿意继续回购']
]

export const filterHistory = [
  { id:1,query:'不含花生及花生制品、50元以内的早餐麦片',conditions:['早餐麦片','排除花生','≤ ¥50','低糖'],time:'今天 10:18',count:8 },
  { id:2,query:'高蛋白、无添加糖的植物奶',conditions:['植物蛋白','蛋白质≥3g','无添加糖'],time:'昨天 19:42',count:5 },
  { id:3,query:'适合下午茶的低糖饼干，配料简单',conditions:['饼干糕点','低糖','配料≤8项'],time:'07-15 14:20',count:12 },
  { id:4,query:'不含乳糖的早餐搭配',conditions:['排除乳糖','早餐场景'],time:'07-11 08:03',count:16 },
  { id:5,query:'钠低于500mg的速食',conditions:['调味速食','钠≤500mg/100g'],time:'07-08 21:16',count:7 },
  { id:6,query:'纯果汁，不要香精和甜味剂',conditions:['果汁饮品','100%果汁','排除香精','排除甜味剂'],time:'07-02 12:28',count:6 },
]

export const anomalies = [
  { id:'EX-1428',type:'未识别成分',target:'桂花小米酥',detail:'复配谷物粉未展开',status:'待分派',owner:'—',time:'10分钟前' },
  { id:'EX-1427',type:'营养单位异常',target:'海盐燕麦曲奇',detail:'钠单位疑似 mg/份',status:'处理中',owner:'赵宁',time:'32分钟前' },
  { id:'EX-1426',type:'图谱关系冲突',target:'燕麦奶-麸质',detail:'两个来源结论不一致',status:'待复核',owner:'知识组',time:'1小时前' },
  { id:'EX-1425',type:'模型处理失败',target:'商家批次 UP-901',detail:'结构化输出校验失败',status:'已重试',owner:'系统',time:'2小时前' },
  { id:'EX-1424',type:'配料缺失',target:'山野莓果棒',detail:'无原始配料文本',status:'待补充',owner:'商家',time:'3小时前' },
  { id:'EX-1423',type:'别名未映射',target:'E322',detail:'建议映射为卵磷脂',status:'待确认',owner:'周研',time:'昨天' },
]

export const reviewTasks = [
  { id:'RV-0872',product:'南瓜籽谷物脆',merchant:'谷本日记',status:'待审核',risk:'2项待确认',submitted:'12分钟前' },
  { id:'RV-0871',product:'无糖杏仁饮',merchant:'植选研究所',status:'知识复核',risk:'别名映射',submitted:'28分钟前' },
  { id:'RV-0870',product:'番茄牛腩饭',merchant:'简食社',status:'需补充',risk:'营养单位',submitted:'1小时前' },
  { id:'RV-0869',product:'可可燕麦曲奇',merchant:'轻负担',status:'待审核',risk:'过敏原提示',submitted:'2小时前' },
  { id:'RV-0868',product:'原味腰果酱',merchant:'坚果森林',status:'已通过',risk:'无',submitted:'昨天' },
]

export const auditLogs = [
  { id:'AL-5129',operator:'顾岚',object:'商品 RV-0868',type:'审核通过',before:'待审核',after:'已通过',time:'今天 09:42',reason:'标签与结构化结果一致' },
  { id:'AL-5128',operator:'周研',object:'成分 E322',type:'别名更新',before:'未映射',after:'卵磷脂',time:'今天 09:18',reason:'依据 GB 2760 标准' },
  { id:'AL-5127',operator:'赵宁',object:'商家 M-032',type:'权限恢复',before:'冻结',after:'正常',time:'昨天 17:06',reason:'资质补充完成' },
  { id:'AL-5126',operator:'顾岚',object:'商品 RV-0864',type:'要求补充',before:'待审核',after:'需补充',time:'昨天 15:42',reason:'原始配料图片不清晰' },
  { id:'AL-5125',operator:'系统',object:'图谱 v2.18.0',type:'版本发布',before:'v2.17.3',after:'v2.18.0',time:'07-16 22:10',reason:'合并12条标准别名' },
  { id:'AL-5124',operator:'周研',object:'花生酱→花生',type:'关系修订',before:'相关于',after:'衍生自',time:'07-16 16:33',reason:'关系语义校准' },
]

export const graphNodes: GraphNode[] = [
  {data:{id:'p1',label:'原味低糖燕麦脆',type:'product',detail:'当前商品 · 已审核'}},
  {data:{id:'oat',label:'全粒燕麦',type:'ingredient',detail:'主要配料 · 38%'}},
  {data:{id:'quinoa',label:'藜麦',type:'ingredient',detail:'主要配料'}},
  {data:{id:'seed',label:'南瓜籽',type:'ingredient',detail:'种子类原料'}},
  {data:{id:'inulin',label:'菊粉',type:'ingredient',detail:'膳食纤维来源'}},
  {data:{id:'fiber',label:'膳食纤维',type:'nutrition',detail:'营养指标'}},
  {data:{id:'gluten',label:'麸质',type:'risk',detail:'燕麦可能存在交叉接触'}},
  {data:{id:'brand',label:'谷本日记',type:'brand',detail:'品牌'}},
  {data:{id:'category',label:'早餐麦片',type:'category',detail:'商品分类'}},
  {data:{id:'rolled',label:'燕麦片',type:'alias',detail:'常见形态/近义词'}},
  {data:{id:'p16',label:'肉桂苹果烤燕麦',type:'related',detail:'关联商品'}},
  {data:{id:'p2',label:'莓果奇亚籽谷物杯',type:'related',detail:'关联商品'}},
]

export const graphEdges: GraphEdge[] = [
  {data:{id:'e1',source:'p1',target:'oat',label:'包含'}},{data:{id:'e2',source:'p1',target:'quinoa',label:'包含'}},
  {data:{id:'e3',source:'p1',target:'seed',label:'包含'}},{data:{id:'e4',source:'p1',target:'inulin',label:'包含'}},
  {data:{id:'e5',source:'inulin',target:'fiber',label:'营养来源'}},{data:{id:'e6',source:'oat',target:'gluten',label:'可能交叉接触'}},
  {data:{id:'e7',source:'p1',target:'brand',label:'属于品牌'}},{data:{id:'e8',source:'p1',target:'category',label:'属于分类'}},
  {data:{id:'e9',source:'oat',target:'rolled',label:'相关形态'}},{data:{id:'e10',source:'oat',target:'p16',label:'关联商品'}},
  {data:{id:'e11',source:'oat',target:'p2',label:'关联商品'}},{data:{id:'e12',source:'quinoa',target:'fiber',label:'含有'}},
]
