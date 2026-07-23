from fastapi import APIRouter, Request

from app.core.responses import SuccessResponse
from app.schemas.catalog import BrandItem, CategoryItem

router = APIRouter()


@router.get(
    "/categories",
    response_model=SuccessResponse[list[CategoryItem]],
    summary="List categories",
    description="Returns active product categories from MySQL.",
)
def categories(request: Request) -> dict:
    items = request.app.state.catalog_service.categories()
    return {"success": True, "data": items, "message": "ok", "request_id": request.state.request_id}


@router.get(
    "/brands",
    response_model=SuccessResponse[list[BrandItem]],
    summary="List brands",
    description="Returns active product brands from MySQL.",
)
def brands(request: Request) -> dict:
    items = request.app.state.catalog_service.brands()
    return {"success": True, "data": items, "message": "ok", "request_id": request.state.request_id}
