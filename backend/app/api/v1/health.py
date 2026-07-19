import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

logger = logging.getLogger(__name__)
router = APIRouter()


def _request_id(request: Request) -> str:
    return request.state.request_id


def _checks(request: Request) -> tuple[str, str]:
    mysql_status = neo4j_status = "ok"
    try:
        with request.app.state.mysql_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        mysql_status = "error"
        logger.warning("MySQL health check failed")
    try:
        with request.app.state.neo4j_driver.session(database=request.app.state.settings.neo4j_database) as session:
            session.run("RETURN 1 AS healthy").consume()
    except Exception:
        neo4j_status = "error"
        logger.warning("Neo4j health check failed")
    return mysql_status, neo4j_status


@router.get("/live", summary="Liveness probe", description="Checks only that the FastAPI process can serve requests.")
def live(request: Request) -> dict:
    return {"success": True, "data": {"service": "ok"}, "message": "alive", "request_id": _request_id(request)}


def _database_health(request: Request, message: str) -> JSONResponse:
    mysql_status, neo4j_status = _checks(request)
    healthy = mysql_status == neo4j_status == "ok"
    content = {
        "success": healthy,
        "data": {"service": "ok", "mysql": mysql_status, "neo4j": neo4j_status},
        "message": message if healthy else "required component unavailable",
        "request_id": _request_id(request),
    }
    return JSONResponse(status_code=200 if healthy else 503, content=content)


@router.get("", summary="Service health", description="Reports service, MySQL, and Neo4j health independently.")
def health(request: Request) -> JSONResponse:
    return _database_health(request, "healthy")


@router.get("/ready", summary="Readiness probe", description="Returns 503 unless both MySQL and Neo4j answer a read query.")
def ready(request: Request) -> JSONResponse:
    return _database_health(request, "ready")
