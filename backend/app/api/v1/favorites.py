from fastapi import APIRouter,Depends,Path,Request,status
from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.favorite import FavoriteCreate,FavoriteItem
router=APIRouter()
@router.get("",response_model=SuccessResponse[list[FavoriteItem]],summary="List my favorites")
def list_favorites(request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.favorite_service.list(user.id),"message":"ok","request_id":request.state.request_id}
@router.post("",response_model=SuccessResponse[FavoriteItem],status_code=status.HTTP_201_CREATED,summary="Add favorite")
def add_favorite(payload:FavoriteCreate,request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.favorite_service.add(user.id,payload.product_code),"message":"created","request_id":request.state.request_id}
@router.delete("/{product_code}",response_model=SuccessResponse[dict],summary="Delete favorite")
def delete_favorite(request:Request,product_code:str=Path(min_length=1,max_length=40),user:UserIdentity=Depends(get_current_user)):
    request.app.state.favorite_service.delete(user.id,product_code);return {"success":True,"data":{"product_code":product_code},"message":"deleted","request_id":request.state.request_id}
