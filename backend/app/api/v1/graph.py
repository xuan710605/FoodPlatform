from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.core.responses import SuccessResponse
from app.schemas.graph import ProductGraph

router = APIRouter()


@router.get(
    "/{product_code}/graph",
    response_model=SuccessResponse[ProductGraph],
    summary="Get product knowledge graph",
    description="Returns a bounded, read-only Cytoscape graph keyed exclusively by stable business codes.",
)
def get_product_graph(
    request: Request,
    product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$", description="Stable product business code")],
) -> dict:
    data = request.app.state.graph_service.get_product_graph(product_code)
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}
