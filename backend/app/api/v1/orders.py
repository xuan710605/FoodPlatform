from fastapi import APIRouter,Depends,Path,Query,Request,status
from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.order import OrderCreate,OrderPage,OrderStatus,OrderSummary,PaymentRequest
router=APIRouter()
@router.post("",response_model=SuccessResponse[OrderSummary],status_code=status.HTTP_201_CREATED,summary="Create order from cart")
def create_order(payload:OrderCreate,request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.create(user.id,payload.model_dump()),"message":"created","request_id":request.state.request_id}
@router.get("",response_model=SuccessResponse[OrderPage],summary="List my orders")
def list_orders(request:Request,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),status:OrderStatus|None=Query(None),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.list(user.id,page,page_size,status),"message":"ok","request_id":request.state.request_id}
@router.get("/{order_id}",response_model=SuccessResponse[OrderSummary],summary="Get my order")
def get_order(request:Request,order_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.get(user.id,order_id),"message":"ok","request_id":request.state.request_id}
@router.post("/{order_id}/pay",response_model=SuccessResponse[OrderSummary],summary="Simulate payment")
def pay_order(payload:PaymentRequest,request:Request,order_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.pay(user.id,order_id,payload.channel),"message":"paid","request_id":request.state.request_id}
@router.post("/{order_id}/cancel",response_model=SuccessResponse[OrderSummary],summary="Cancel order and restore inventory")
def cancel_order(request:Request,order_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.cancel(user.id,order_id),"message":"cancelled","request_id":request.state.request_id}

@router.post("/{order_id}/confirm-receipt",response_model=SuccessResponse[OrderSummary],summary="Confirm receipt")
def confirm_receipt(request:Request,order_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.order_service.confirm_receipt(user.id,order_id),"message":"completed","request_id":request.state.request_id}