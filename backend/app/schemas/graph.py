from typing import Literal

from pydantic import BaseModel, Field


class CytoscapeNodeData(BaseModel):
    id: str
    type: str
    business_code: str
    label: str
    risk_level: str | None = None


class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    type: str
    confidence: float | None = None
    source_code: str | None = None
    audit_status: str | None = None


class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData


class GraphSummary(BaseModel):
    contains_count: int = Field(ge=0)
    may_contain_count: int = Field(ge=0)
    risk_count: int = Field(ge=0)
    information_status: Literal["SUFFICIENT", "INSUFFICIENT", "NOT_SYNCED"]


class ProductGraph(BaseModel):
    nodes: list[CytoscapeNode]
    edges: list[CytoscapeEdge]
    summary: GraphSummary
