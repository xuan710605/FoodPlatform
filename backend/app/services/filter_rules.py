import re
from decimal import Decimal

from app.core.filter_categories import CATEGORY_CODE_ALIASES, VALID_CATEGORY_CODES
from app.schemas.filter import FilterAnalyzeResult, NutritionTarget


NEGATION_MARKERS = ("不想吃", "不想要", "不含", "不要", "避免", "排除", "去掉", "避开", "不能含")
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
CATEGORY_SYNONYMS = CATEGORY_CODE_ALIASES
EXCLUDABLE_CATEGORY_CODES = VALID_CATEGORY_CODES

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
            if alias in INGREDIENT_SYNONYMS and category_code != "CAT005":
                ingredients.append(INGREDIENT_SYNONYMS[alias])
            elif category_code in EXCLUDABLE_CATEGORY_CODES:
                categories.append(category_code)
            positive_text = re.sub(pattern, " ", positive_text)
    return list(dict.fromkeys(ingredients)), list(dict.fromkeys(categories)), positive_text


class ControlledFilterAnalyzer:
    def analyze(self, text: str) -> FilterAnalyzeResult:
        normalized = " ".join(text.strip().split())
        exclusions, excluded_categories, positive_text = _negated_matches(normalized)
        targets: list[NutritionTarget] = []
        preferred = [name for name in ("高蛋白",) if name in normalized]
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
            preferred_ingredients=preferred,
            nutrition_targets=targets,
            max_price=Decimal(price_match.group(1)) if price_match else None,
            category_code=category_code,
            unparsed_fragments=[] if recognized else [normalized],
        )
