import json
from typing import Any

import httpx
from pydantic import ConfigDict

from app.schemas.filter import FilterConditions


class QwenAnalysisError(RuntimeError):
    """Sanitized Qwen failure; never includes credentials or raw response bodies."""


class QwenFilterPayload(FilterConditions):
    model_config = ConfigDict(extra="forbid")


class QwenFilterAnalyzer:
    def __init__(self, client: httpx.Client, api_key: str, model: str, base_url: str, timeout_seconds: float):
        self._client = client
        self._api_key = api_key
        self._model = model
        base = base_url.rstrip("/")
        self._url = base if base.endswith("/chat/completions") else base + "/chat/completions"
        self._timeout = timeout_seconds

    def analyze(self, text: str) -> FilterConditions:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        try:
            response = self._client.post(
                self._url,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            body: dict[str, Any] = response.json()
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise ValueError("Qwen content must be a JSON string")
            return QwenFilterPayload.model_validate(json.loads(content))
        except Exception as exc:
            raise QwenAnalysisError("Qwen analysis failed") from exc

    @staticmethod
    def _system_prompt() -> str:
        return """你是食品筛选条件解析器。只输出 JSON 对象，不要 Markdown 或解释。字段必须且只能是：
exclude_ingredients（字符串数组）、exclude_categories（字符串数组，元素只能是 CAT001 至 CAT010，禁止分类名称）、preferred_ingredients（字符串数组）、
nutrition_targets（数组，每项包含 nutrient_code、nutrient_name、operator、value、unit、basis）、
max_price（数字或 null）、category_code（字符串或 null）。
category_code 仅允许 CAT001 至 CAT010；operator 仅允许 LTE 或 GTE；
basis 仅允许 PER_100G 或 PER_100ML。
不要判断商品是否安全，不要输出商品结果。未明确表达的条件使用空数组或 null。"""
