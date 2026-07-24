from app.schemas.filter import FilterAnalyzeResult, FilterConditions, NutritionTarget
from app.services.filter_rules import ControlledFilterAnalyzer
from app.services.qwen_filter_analyzer import QwenAnalysisError, QwenFilterAnalyzer


class FilterAnalyzerOrchestrator:
    def __init__(self, controlled: ControlledFilterAnalyzer, qwen: QwenFilterAnalyzer | None, enabled: bool):
        self.controlled = controlled
        self.qwen = qwen
        self.enabled = enabled

    def analyze(self, text: str) -> FilterAnalyzeResult:
        rules = self.controlled.analyze(text)
        if not self.enabled:
            return rules
        if self.qwen is None:
            return rules.model_copy(update={"parser": "CONTROLLED_RULES_FALLBACK", "fallback_reason": "QWEN_NOT_CONFIGURED"})
        try:
            qwen = self.qwen.analyze(text)
        except QwenAnalysisError:
            return rules.model_copy(update={"parser": "CONTROLLED_RULES_FALLBACK", "fallback_reason": "QWEN_UNAVAILABLE"})
        return self._merge(rules, qwen)

    @staticmethod
    def _merge(rules: FilterAnalyzeResult, qwen: FilterConditions) -> FilterAnalyzeResult:
        exclusions = list(dict.fromkeys(rules.exclude_ingredients + qwen.exclude_ingredients))
        excluded_categories = list(dict.fromkeys(rules.exclude_categories + qwen.exclude_categories))
        preferred = list(dict.fromkeys(rules.preferred_ingredients + qwen.preferred_ingredients))
        targets: list[NutritionTarget] = list(rules.nutrition_targets)
        protected_codes = {target.nutrient_code for target in targets if target.nutrient_code}
        protected_names = {target.nutrient_name for target in targets}
        targets.extend(
            target
            for target in qwen.nutrition_targets
            if target.nutrient_code not in protected_codes and target.nutrient_name not in protected_names
        )
        conditions_present = bool(exclusions or excluded_categories or preferred or targets or rules.max_price is not None or qwen.max_price is not None or rules.category_code or qwen.category_code)
        return FilterAnalyzeResult(
            normalized_text=rules.normalized_text,
            exclude_ingredients=exclusions,
            exclude_categories=excluded_categories,
            preferred_ingredients=preferred,
            nutrition_targets=targets,
            max_price=rules.max_price if rules.max_price is not None else qwen.max_price,
            category_code=rules.category_code or qwen.category_code,
            parser="QWEN_MERGED",
            qwen_used=True,
            fallback_reason=None,
            unparsed_fragments=[] if conditions_present else rules.unparsed_fragments,
        )
