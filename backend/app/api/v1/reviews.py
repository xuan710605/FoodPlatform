from fastapi import APIRouter,Depends,Query,Request,status
from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.review import ReviewCreate,ReviewItem,ReviewPage
router=APIRouter()
@router.get("/products/{product_code}/reviews",response_model=SuccessResponse[ReviewPage],summary="List published product reviews")
def product_reviews(product_code:str,request:Request,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):return {"success":True,"data":request.app.state.review_service.list_product(product_code,page,page_size),"message":"ok","request_id":request.state.request_id}
@router.get("/reviews/me",response_model=SuccessResponse[ReviewPage],summary="List my reviews")
def my_reviews(request:Request,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.review_service.list_user(user.id,page,page_size),"message":"ok","request_id":request.state.request_id}
@router.post("/reviews",response_model=SuccessResponse[ReviewItem],status_code=status.HTTP_201_CREATED,summary="Review a completed order item")
def create_review(payload:ReviewCreate,request:Request,user:UserIdentity=Depends(get_current_user)):return {"success":True,"data":request.app.state.review_service.create(user.id,payload.model_dump()),"message":"created","request_id":request.state.request_id}