from fastapi import APIRouter,Depends,Path,Request,status
from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.cart import CartItem,CartItemCreate,CartItemUpdate,CartSummary
router=APIRouter()
@router.get("",response_model=SuccessResponse[CartSummary],summary="Get current cart")
def get_cart(request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.cart_service.get(user.id),"message":"ok","request_id":request.state.request_id}
@router.post("/items",response_model=SuccessResponse[CartItem],status_code=status.HTTP_201_CREATED,summary="Add cart item")
def add_item(payload:CartItemCreate,request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.cart_service.add(user.id,payload.model_dump()),"message":"created","request_id":request.state.request_id}
@router.put("/items/{item_id}",response_model=SuccessResponse[CartItem],summary="Update cart item quantity")
def update_item(payload:CartItemUpdate,request:Request,item_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.cart_service.update(user.id,item_id,payload.quantity),"message":"updated","request_id":request.state.request_id}
@router.delete("/items/{item_id}",response_model=SuccessResponse[dict],summary="Delete cart item")
def delete_item(request:Request,item_id:int=Path(gt=0),user:UserIdentity=Depends(get_current_user)):
    request.app.state.cart_service.delete(user.id,item_id);return {"success":True,"data":{"id":item_id},"message":"deleted","request_id":request.state.request_id}
