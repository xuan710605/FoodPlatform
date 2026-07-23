import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging, request_id_context
from app.db.mysql import create_mysql_engine, create_session_factory
from app.db.neo4j import create_neo4j_driver
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.commerce_repository import CommerceRepository
from app.repositories.filter_repository import FilterGraphRepository
from app.repositories.graph_repository import GraphRepository
from app.repositories.preference_repository import PreferenceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.catalog_service import CatalogService
from app.services.filter_rules import ControlledFilterAnalyzer
from app.services.filter_service import FilterService
from app.services.graph_service import GraphService
from app.services.preference_service import PreferenceService
from app.services.product_service import ProductService

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s version %s", settings.app_name, __version__)
    engine = create_mysql_engine(settings)
    driver = create_neo4j_driver(settings)
    session_factory = create_session_factory(engine)
    product_repository = ProductRepository(session_factory)
    user_repository = UserRepository(session_factory)
    app.state.settings = settings
    app.state.mysql_engine = engine
    app.state.neo4j_driver = driver
    app.state.product_service = ProductService(product_repository)
    app.state.auth_service = AuthService(user_repository, settings)
    app.state.preference_service = PreferenceService(PreferenceRepository(session_factory))
    app.state.catalog_service = CatalogService(CatalogRepository(session_factory))
    commerce_repository = CommerceRepository(session_factory)
    app.state.cart_service = CartService(commerce_repository)
    app.state.order_service = OrderService(commerce_repository)
    app.state.graph_service = GraphService(
        product_repository,
        GraphRepository(driver, settings.neo4j_database),
    )
    app.state.filter_service = FilterService(
        product_repository,
        FilterGraphRepository(driver, settings.neo4j_database),
        ControlledFilterAnalyzer(),
    )
    try:
        yield
    finally:
        driver.close()
        engine.dispose()
        logger.info("Stopped %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Authentication, user preferences, catalog, product, and knowledge graph API for FoodPlatform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    responses={
        404: {"description": "Resource not found", "content": {"application/json": {"example": {"success": False, "error": {"code": "PRODUCT_NOT_FOUND", "message": "Product not found", "details": None}, "request_id": "request-id"}}}},
        500: {"description": "Internal server error", "content": {"application/json": {"example": {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Internal server error", "details": None}, "request_id": "request-id"}}}},
        503: {"description": "Required database unavailable", "content": {"application/json": {"example": {"success": False, "error": {"code": "MYSQL_UNAVAILABLE", "message": "Product database is unavailable", "details": None}, "request_id": "request-id"}}}},
    },
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type", "X-Request-ID"],
)
install_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    token = request_id_context.set(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info("request method=%s path=%s elapsed_ms=%.2f", request.method, request.url.path, elapsed_ms)
        request_id_context.reset(token)


@app.get("/", tags=["Health"], summary="API information", description="Returns service metadata and documentation links.")
def root(request: Request) -> dict:
    return {
        "success": True,
        "data": {"service": settings.app_name, "version": __version__, "docs": "/docs", "redoc": "/redoc"},
        "message": "ok",
        "request_id": request.state.request_id,
    }
