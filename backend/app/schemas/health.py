from typing import Literal

from pydantic import BaseModel


class HealthStatus(BaseModel):
    service: Literal["ok"] = "ok"
    mysql: Literal["ok", "error"]
    neo4j: Literal["ok", "error"]


class LiveStatus(BaseModel):
    service: Literal["ok"] = "ok"
