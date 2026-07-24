from fastapi import APIRouter,Depends,Request
from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.insight import RecommendationItem,NotificationItem
router=APIRouter()
@router.get('/recommendations',response_model=SuccessResponse[list[RecommendationItem]],summary='Explainable recommendations for current user')
def recommendations(request:Request,user:UserIdentity=Depends(get_current_user)):return {'success':True,'data':request.app.state.insight_service.recommendations(user.id),'message':'ok','request_id':request.state.request_id}
@router.get('/notifications',response_model=SuccessResponse[list[NotificationItem]],summary='Notifications derived from current user orders')
def notifications(request:Request,user:UserIdentity=Depends(get_current_user)):return {'success':True,'data':request.app.state.insight_service.notifications(user.id),'message':'ok','request_id':request.state.request_id}