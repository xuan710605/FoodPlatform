import re
from decimal import Decimal

from app.schemas.filter import FilterAnalyzeResult, NutritionTarget


NEGATION_MARKERS = ("不含", "不要", "避免", "排除", "去掉", "避开", "不能含")
INGREDIENT_SYNONYMS = {
    "花生酱": "花生",
    "花生粉": "花生",
    "花生": "花生",
    "鲜奶": "牛奶",
    "奶制品": "牛奶",
    "乳品": "牛奶",
    "牛奶": "牛奶",
    "乳糖": "乳糖",
    "大豆": "大豆",
    "小麦": "小麦",
    "麸质": "麸质",
    "鸡蛋": "鸡蛋",
    "芝麻": "芝麻",
    "杏仁": "杏仁",
    "核桃": "核桃",
    "腰果": "腰果",
}
CATEGORY_SYNONYMS = {
    "早餐麦片": "CAT001",
    "早餐": "CAT001",
    "饼干": "CAT002",
    "奶制品": "CAT003",
    "乳品": "CAT003",
    "鲜奶": "CAT003",
    "酸奶": "CAT003",
    "牛奶": "CAT003",
    "坚果": "CAT004",
    "果汁饮料": "CAT005",
    "果汁": "CAT005",
    "面包": "CAT006",
    "巧克力": "CAT007",
    "速食": "CAT008",
    "谷物棒": "CAT009",
    "植物蛋白": "CAT010",
    "植物奶": "CAT010",
}
EXCLUDABLE_CATEGORY_CODES = {"CAT005"}
NUTRIENT_RULES = {
    "低糖": NutritionTarget(nutrient_code="NUT_SUGAR", nutrient_name="糖", operator="LTE", value=Decimal("5"), unit="g"),
    "低钠": NutritionTarget(nutrient_code="NUT_SODIUM", nutrient_name="钠", operator="LTE", value=Decimal("500"), unit="mg"),
    "高蛋白": NutritionTarget(nutrient_code="NUT_PROTEIN", nutrient_name="蛋白质", operator="GTE", value=Decimal("8"), unit="g"),
}


def _negated_matches(text: str) -> tuple[list[str], list[str], str]:
    ingredients: list[str] = []
    categories: list[str] = []
    positive_text = text
    aliases = sorted(set(INGREDIENT_SYNONYMS) | set(CATEGORY_SYNONYMS), key=len, reverse=True)
    for marker in NEGATION_MARKERS:
        for alias in aliases:
            pattern = rf"{re.escape(marker)}\s*{re.escape(alias)}"
            if not re.search(pattern, positive_text):
                continue
            category_code = CATEGORY_SYNONYMS.get(alias)
            if category_code in EXCLUDABLE_CATEGORY_CODES:
                categories.append(category_code)
            elif alias in INGREDIENT_SYNONYMS:
                ingredients.append(INGREDIENT_SYNONYMS[alias])
            positive_text = re.sub(pattern, " ", positive_text)
    return list(dict.fromkeys(ingredients)), list(dict.fromkeys(categories)), positive_text


class ControlledFilterAnalyzer:
    def analyze(self, text: str) -> FilterAnalyzeResult:
        normalized = " ".join(text.strip().split())
        exclusions, excluded_categories, positive_text = _negated_matches(normalized)
        targets = [rule.model_copy(deep=True) for name, rule in NUTRIENT_RULES.items() if name in normalized]
        explicit_patterns = [
            ("糖", "NUT_SUGAR", "g"), ("钠", "NUT_SODIUM", "mg"),
            ("脂肪", "NUT_FAT", "g"), ("蛋白质", "NUT_PROTEIN", "g"),
        ]
        for name, code, unit in explicit_patterns:
            match = re.search(rf"{name}[^0-9]{{0,8}}(?:不超过|低于|≤|小于)\s*(\d+(?:\.\d+)?)", normalized)
            if match:
                targets = [target for target in targets if target.nutrient_code != code]
                targets.append(NutritionTarget(nutrient_code=code, nutrient_name=name, operator="LTE", value=Decimal(match.group(1)), unit=unit))
            match = re.search(rf"{name}[^0-9]{{0,8}}(?:不少于|高于|≥|大于)\s*(\d+(?:\.\d+)?)", normalized)
            if match:
                targets = [target for target in targets if target.nutrient_code != code]
                targets.append(NutritionTarget(nutrient_code=code, nutrient_name=name, operator="GTE", value=Decimal(match.group(1)), unit=unit))
        price_match = re.search(r"(\d+(?:\.\d+)?)\s*元?(?:以内|以下|以下的|封顶)?", normalized)
        category_code = next(
            (code for name, code in sorted(CATEGORY_SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True) if name in positive_text),
            None,
        )
        recognized = exclusions or excluded_categories or targets or price_match or category_code
        return FilterAnalyzeResult(
            normalized_text=normalized,
            exclude_ingredients=exclusions,
            exclude_categories=excluded_categories,
            nutrition_targets=targets,
            max_price=Decimal(price_match.group(1)) if price_match else None,
            category_code=category_code,
            unparsed_fragments=[] if recognized else [normalized],
        )
