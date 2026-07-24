from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.core.responses import SuccessResponse
from app.dependencies.auth import require_role
from app.schemas.auth import UserIdentity
from app.schemas.workspace import (
    AdminDashboard, AdminProductItem, AdminUserItem, AdminUserStatusUpdate, MerchantDashboard,
    MerchantOrderItem, MerchantOrderStatusUpdate, MerchantProductItem,
    MerchantProductWrite, ProductApproval, SaleStatusUpdate,
)

router = APIRouter()
merchant_only = require_role("MERCHANT")
admin_only = require_role("ADMIN")


def response(request: Request, data: object, message: str = "ok") -> dict:
    return {"success": True, "data": data, "message": message, "request_id": request.state.request_id}


@router.get("/merchant/dashboard", response_model=SuccessResponse[MerchantDashboard], tags=["Merchant"])
def merchant_dashboard(request: Request, user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.merchant_dashboard(user.id))


@router.get("/merchant/products", response_model=SuccessResponse[list[MerchantProductItem]], tags=["Merchant"])
def merchant_products(request: Request, user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.merchant_products(user.id))


@router.post("/merchant/products", response_model=SuccessResponse[dict], status_code=status.HTTP_201_CREATED, tags=["Merchant"])
def merchant_product_create(request: Request, payload: MerchantProductWrite, user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.create_product(user.id, payload.model_dump()), "created")


@router.put("/merchant/products/{product_code}", response_model=SuccessResponse[dict], tags=["Merchant"])
def merchant_product_update(request: Request, payload: MerchantProductWrite, product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$")], user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.update_product(user.id, product_code, payload.model_dump()), "updated")


@router.put("/merchant/products/{product_code}/sale-status", response_model=SuccessResponse[dict], tags=["Merchant"])
def merchant_product_sale_status(request: Request, payload: SaleStatusUpdate, product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$")], user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.update_sale_status(user.id, product_code, payload.sale_status), "updated")


@router.get("/merchant/orders", response_model=SuccessResponse[list[MerchantOrderItem]], tags=["Merchant"])
def merchant_orders(request: Request, user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.merchant_orders(user.id))


@router.put("/merchant/orders/{order_id}/status", response_model=SuccessResponse[dict], tags=["Merchant"])
def merchant_order_status(request: Request, payload: MerchantOrderStatusUpdate, order_id: Annotated[int, Path(gt=0)], user: UserIdentity = Depends(merchant_only)) -> dict:
    return response(request, request.app.state.workspace_service.update_order_status(user.id, order_id, payload.status), "updated")


@router.get("/admin/dashboard", response_model=SuccessResponse[AdminDashboard], tags=["Admin"])
def admin_dashboard(request: Request, _user: UserIdentity = Depends(admin_only)) -> dict:
    return response(request, request.app.state.workspace_service.admin_dashboard())


@router.get("/admin/users", response_model=SuccessResponse[list[AdminUserItem]], tags=["Admin"])
def admin_users(request: Request, keyword: Annotated[str | None, Query(min_length=1, max_length=128)] = None, _user: UserIdentity = Depends(admin_only)) -> dict:
    return response(request, request.app.state.workspace_service.admin_users(keyword))


@router.put("/admin/users/{user_id}/status", response_model=SuccessResponse[dict], tags=["Admin"])
def admin_user_status(request: Request, payload: AdminUserStatusUpdate, user_id: Annotated[int, Path(gt=0)], _user: UserIdentity = Depends(admin_only)) -> dict:
    return response(request, request.app.state.workspace_service.update_admin_user_status(user_id, payload.status), "updated")


@router.get("/admin/products", response_model=SuccessResponse[list[AdminProductItem]], tags=["Admin"])
def admin_products(request: Request, review_status: Annotated[Literal["PENDING", "APPROVED", "REJECTED", "NEED_MORE_INFO"] | None, Query()] = "PENDING", _user: UserIdentity = Depends(admin_only)) -> dict:
    return response(request, request.app.state.workspace_service.admin_products(review_status))


@router.put("/admin/products/{product_code}/approve", response_model=SuccessResponse[dict], tags=["Admin"])
def admin_product_approve(request: Request, payload: ProductApproval, product_code: Annotated[str, Path(pattern=r"^FP\d{4,}$")], user: UserIdentity = Depends(admin_only)) -> dict:
    return response(request, request.app.state.workspace_service.approve_product(user.id, product_code, payload.opinion), "approved")