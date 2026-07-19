from fastapi import APIRouter

from app.api.v1 import graph, health, products

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(graph.router, prefix="/products", tags=["Graph"])
