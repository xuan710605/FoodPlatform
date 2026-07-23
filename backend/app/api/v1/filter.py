from fastapi import APIRouter, Request

from app.core.responses import SuccessResponse
from app.schemas.filter import FilterAnalyzeRequest, FilterAnalyzeResult, FilterSearchRequest, FilterSearchResult

router = APIRouter()


@router.post("/analyze", response_model=SuccessResponse[FilterAnalyzeResult], summary="Analyze food filter text", description="Parses supported food constraints with deterministic controlled rules; no Qwen or external model is called.")
def analyze_filter(request: Request, payload: FilterAnalyzeRequest) -> dict:
    data = request.app.state.filter_service.analyze(payload.text)
    return {"success":True,"data":data,"message":"analyzed","request_id":request.state.request_id}


@router.post("/search", response_model=SuccessResponse[FilterSearchResult], summary="Search food by ingredients and nutrition", description="Combines audited MySQL product facts with Neo4j ingredient aliases, derivatives, and risk evidence.")
def search_filter(request: Request, payload: FilterSearchRequest) -> dict:
    data = request.app.state.filter_service.search(payload)
    return {"success":True,"data":data,"message":"ok","request_id":request.state.request_id}