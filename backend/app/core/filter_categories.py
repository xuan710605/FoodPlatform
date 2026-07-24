VALID_CATEGORY_CODES = {f"CAT{index:03d}" for index in range(1, 11)}

CATEGORY_CODE_ALIASES = {
    "早餐麦片": "CAT001", "早餐": "CAT001",
    "饼干糕点": "CAT002", "饼干": "CAT002", "糕点": "CAT002",
    "乳品酸奶": "CAT003", "奶制品": "CAT003", "乳品": "CAT003", "鲜奶": "CAT003", "酸奶": "CAT003", "牛奶": "CAT003",
    "坚果果干": "CAT004", "坚果": "CAT004", "果干": "CAT004",
    "果汁饮品": "CAT005", "果汁饮料": "CAT005", "果汁": "CAT005",
    "面包烘焙": "CAT006", "烘焙食品": "CAT006", "面包": "CAT006",
    "巧克力": "CAT007",
    "调味速食": "CAT008", "速食": "CAT008", "调味品": "CAT008",
    "谷物能量棒": "CAT009", "谷物棒": "CAT009", "能量棒": "CAT009",
    "植物蛋白": "CAT010", "植物奶": "CAT010",
}


def normalize_category_code(value: str) -> str:
    normalized = value.strip()
    code = normalized.upper()
    if code in VALID_CATEGORY_CODES:
        return code
    if normalized in CATEGORY_CODE_ALIASES:
        return CATEGORY_CODE_ALIASES[normalized]
    raise ValueError(f"Unknown category code or name: {normalized}")


def normalize_category_codes(values: list[str]) -> list[str]:
    return list(dict.fromkeys(normalize_category_code(value) for value in values))
