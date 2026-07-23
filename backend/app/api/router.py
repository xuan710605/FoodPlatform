from fastapi import APIRouter

from app.api.v1 import auth, catalog, filter, graph, health, preferences, products, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
api_router.include_router(catalog.router, tags=["Catalog"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(graph.router, prefix="/products", tags=["Graph"])
api_router.include_router(filter.router, prefix="/filter", tags=["Filter"])
