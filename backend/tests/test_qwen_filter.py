import json

import httpx

from app.services.filter_analyzer import FilterAnalyzerOrchestrator
from app.services.filter_rules import ControlledFilterAnalyzer
from app.services.qwen_filter_analyzer import QwenFilterAnalyzer


class FakeResponse:
    def __init__(self, content: str, status_code: int = 200):
        self.status_code = status_code
        self._body = {"choices": [{"message": {"content": content}}]}
        self.request = httpx.Request("POST", "https://qwen.example.test/chat/completions")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            response = httpx.Response(self.status_code, request=self.request)
            raise httpx.HTTPStatusError("upstream failure", request=self.request, response=response)

    def json(self) -> dict:
        return self._body


class FakeClient:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.last_request: dict | None = None

    def post(self, url: str, **kwargs):
        self.last_request = {"url": url, **kwargs}
        if self.error is not None:
            raise self.error
        assert self.response is not None
        return self.response


def qwen_payload(**overrides) -> str:
    payload = {
        "exclude_ingredients": [],
        "exclude_categories": [],
        "preferred_ingredients": ["配料简单"],
        "nutrition_targets": [],
        "max_price": None,
        "category_code": "CAT001",
    }
    payload.update(overrides)
    return json.dumps(payload, ensure_ascii=False)


def build_orchestrator(client: FakeClient) -> FilterAnalyzerOrchestrator:
    qwen = QwenFilterAnalyzer(
        client=client,
        api_key="unit-test-secret",
        model="qwen-test",
        base_url="https://qwen.example.test/v1",
        timeout_seconds=8,
    )
    return FilterAnalyzerOrchestrator(ControlledFilterAnalyzer(), qwen, enabled=True)


def test_qwen_success_merges_without_overriding_rule_hard_conditions():
    client = FakeClient(FakeResponse(qwen_payload(
        exclude_ingredients=["芝麻"],
        nutrition_targets=[{
            "nutrient_code": "NUT_SUGAR", "nutrient_name": "糖", "operator": "LTE",
            "value": 99, "unit": "g", "basis": "PER_100G",
        }],
    )))

    result = build_orchestrator(client).analyze("不要花生，糖不超过8g的早餐麦片")

    assert result.parser == "QWEN_MERGED"
    assert result.qwen_used is True
    assert "花生" in result.exclude_ingredients
    assert "芝麻" in result.exclude_ingredients
    sugar = next(item for item in result.nutrition_targets if item.nutrient_name == "糖")
    assert sugar.value == 8
    assert result.category_code == "CAT001"
    assert client.last_request is not None
    assert client.last_request["json"]["response_format"] == {"type": "json_object"}
    assert client.last_request["headers"]["Authorization"] == "Bearer unit-test-secret"


def test_qwen_timeout_falls_back_to_controlled_rules():
    client = FakeClient(error=httpx.TimeoutException("timed out"))

    result = build_orchestrator(client).analyze("不要花生")

    assert result.parser == "CONTROLLED_RULES_FALLBACK"
    assert result.qwen_used is False
    assert result.fallback_reason == "QWEN_UNAVAILABLE"
    assert "花生" in result.exclude_ingredients


def test_qwen_invalid_json_falls_back_to_controlled_rules():
    result = build_orchestrator(FakeClient(FakeResponse("not-json"))).analyze("高蛋白牛奶")

    assert result.parser == "CONTROLLED_RULES_FALLBACK"
    assert result.fallback_reason == "QWEN_UNAVAILABLE"
    assert result.category_code is not None


def test_qwen_schema_error_falls_back_to_controlled_rules():
    invalid = qwen_payload(unexpected_field="not allowed")

    result = build_orchestrator(FakeClient(FakeResponse(invalid))).analyze("早餐麦片")

    assert result.parser == "CONTROLLED_RULES_FALLBACK"
    assert result.fallback_reason == "QWEN_UNAVAILABLE"


def test_missing_qwen_key_uses_controlled_fallback_without_network():
    orchestrator = FilterAnalyzerOrchestrator(ControlledFilterAnalyzer(), qwen=None, enabled=True)

    result = orchestrator.analyze("不要花生")

    assert result.parser == "CONTROLLED_RULES_FALLBACK"
    assert result.fallback_reason == "QWEN_NOT_CONFIGURED"
    assert "花生" in result.exclude_ingredients
