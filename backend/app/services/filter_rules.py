import re
from decimal import Decimal

from app.schemas.filter import FilterAnalyzeResult, NutritionTarget


INGREDIENT_TERMS = (
    "花生酱", "花生粉", "花生", "牛奶", "乳糖", "大豆", "小麦", "麸质", "鸡蛋", "芝麻", "杏仁", "核桃", "腰果"
)
CATEGORY_CODES = {
    "早餐麦片": "CAT001", "饼干": "CAT002", "酸奶": "CAT003", "牛奶": "CAT003",
    "坚果": "CAT004", "果汁": "CAT005", "面包": "CAT006", "巧克力": "CAT007",
    "速食": "CAT008", "谷物棒": "CAT009", "植物蛋白": "CAT010", "植物奶": "CAT010",
}
NUTRIENT_RULES = {
    "低糖": NutritionTarget(nutrient_code="NUT_SUGAR", nutrient_name="糖", operator="LTE", value=Decimal("5"), unit="g"),
    "低钠": NutritionTarget(nutrient_code="NUT_SODIUM", nutrient_name="钠", operator="LTE", value=Decimal("500"), unit="mg"),
    "高蛋白": NutritionTarget(nutrient_code="NUT_PROTEIN", nutrient_name="蛋白质", operator="GTE", value=Decimal("8"), unit="g"),
}


class ControlledFilterAnalyzer:
    def analyze(self, text: str) -> FilterAnalyzeResult:
        normalized = " ".join(text.strip().split())
        exclusions = []
        exclusion_context = any(marker in normalized for marker in ("不含", "不要", "排除", "避开", "不能含"))
        if exclusion_context:
            exclusions = [term for term in INGREDIENT_TERMS if term in normalized]
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
        price_match = re.search(r"(\d+(?:\.\d+)?)\s*元(?:以内|以下|以下的|内|封顶)?", normalized)
        category_code = next((code for name, code in CATEGORY_CODES.items() if name in normalized), None)
        return FilterAnalyzeResult(
            normalized_text=normalized,
            exclude_ingredients=list(dict.fromkeys(exclusions)),
            nutrition_targets=targets,
            max_price=Decimal(price_match.group(1)) if price_match else None,
            category_code=category_code,
            unparsed_fragments=[] if exclusions or targets or price_match or category_code else [normalized],
        )