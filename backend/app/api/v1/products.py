from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Request

from app.core.responses import SuccessResponse
from app.schemas.common import Page
from app.schemas.product import ProductDetail, ProductListItem
from app.schemas.product_query import CategoryProductCount, ProductQuery

router = APIRouter()


@router.get(
    "",
    response_model=SuccessResponse[Page[ProductListItem]],
    summary="List products",
    description="Returns approved, non-deleted consumer products using bounded pagination and whitelisted sorting.",
)
def list_products(
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    keyword: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
    category_code: Annotated[str | None, Query(max_length=32)] = None,
    brand: Annotated[str | None, Query(max_length=100)] = None,
    brand_code: Annotated[str | None, Query(max_length=32)] = None,
    exclude: Annotated[list[str] | None, Query()] = None,
    sugar_max: Annotated[Decimal | None, Query(ge=0)] = None,
    fat_max: Annotated[Decimal | None, Query(ge=0)] = None,
    protein_min: Annotated[Decimal | None, Query(ge=0)] = None,
    sodium_max: Annotated[Decimal | None, Query(ge=0)] = None,
    price_min: Annotated[Decimal | None, Query(ge=0)] = None,
    price_max: Annotated[Decimal | None, Query(ge=0)] = None,
    merchant_id: Annotated[int | None, Query(gt=0)] = None,
    status: Annotated[Literal["ON_SALE", "OFF_SALE", "SUSPENDED"] | None, Query()] = None,
    sort_by: Annotated[Literal["created_at", "updated_at", "name", "price", "stock"], Query()] = "created_at",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> dict:
    query = ProductQuery(page=page,page_size=page_size,keyword=keyword,category=category,
        category_code=category_code,brand=brand,brand_code=brand_code,
        excluded_ingredients=exclude or [],sugar_max=sugar_max,fat_max=fat_max,
        protein_min=protein_min,sodium_max=sodium_max,price_min=price_min,
        price_max=price_max,merchant_id=merchant_id,status=status,sort_by=sort_by,sort_order=sort_order)
    data = request.app.state.product_service.list_products(query.model_dump())
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}


@router.get("/categories",response_model=SuccessResponse[list[CategoryProductCount]],summary="Product counts by category")
def product_categories(request: Request) -> dict:
    data=request.app.state.product_service.category_stats()
    return {"success":True,"data":data,"message":"ok","request_id":request.state.request_id}


@router.get(
    "/{product_code}",
    response_model=SuccessResponse[ProductDetail],
    summary="Get product detail",
    description="Returns MySQL product facts, sales and review aggregates, evidence, approved structured ingredients, specifications, prices and nutrition.",
)
def get_product(
    request: Request,
    product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$", description="Stable product business code")],
) -> dict:
    data = request.app.state.product_service.get_detail(product_code)
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}
