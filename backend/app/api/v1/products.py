from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Request

from app.core.responses import SuccessResponse
from app.schemas.common import Page
from app.schemas.product import ProductDetail, ProductListItem

router = APIRouter()


@router.get(
    "",
    response_model=SuccessResponse[Page[ProductListItem]],
    summary="List products",
    description="Returns approved, non-deleted consumer products using bounded pagination and whitelisted sorting.",
)
def list_products(
    request: Request,
    page: Annotated[int, Query(ge=1, description="One-based page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page, maximum 100")] = 20,
    keyword: Annotated[str | None, Query(max_length=100, description="Product name or product code fragment")] = None,
    category_code: Annotated[str | None, Query(max_length=32)] = None,
    brand_code: Annotated[str | None, Query(max_length=32)] = None,
    merchant_id: Annotated[int | None, Query(gt=0)] = None,
    status: Annotated[Literal["ON_SALE", "OFF_SALE", "SUSPENDED"] | None, Query(description="Sale status; defaults to ON_SALE")] = None,
    sort_by: Annotated[Literal["created_at", "updated_at", "name", "price", "stock"], Query(description="Whitelisted sort field")] = "created_at",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> dict:
    data = request.app.state.product_service.list_products(
        {
            "page": page,
            "page_size": page_size,
            "keyword": keyword,
            "category_code": category_code,
            "brand_code": brand_code,
            "merchant_id": merchant_id,
            "status": status,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
    )
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}


@router.get(
    "/{product_code}",
    response_model=SuccessResponse[ProductDetail],
    summary="Get product detail",
    description="Returns MySQL product facts, raw ingredients, approved structured ingredients, specifications, prices and nutrition.",
)
def get_product(
    request: Request,
    product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$", description="Stable product business code")],
) -> dict:
    data = request.app.state.product_service.get_detail(product_code)
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}
