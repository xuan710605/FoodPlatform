from typing import Any

from neo4j.exceptions import Neo4jError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.graph_repository import GraphRepository
from app.repositories.product_repository import ProductRepository


class GraphService:
    def __init__(self, product_repository: ProductRepository, graph_repository: GraphRepository):
        self.product_repository = product_repository
        self.graph_repository = graph_repository

    def get_product_graph(self, product_code: str) -> dict[str, Any]:
        try:
            exists = self.product_repository.exists(product_code)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Product database is unavailable", 503) from exc
        if not exists:
            raise AppError("PRODUCT_NOT_FOUND", "Product not found", 404)
        try:
            graph = self.graph_repository.get_product_graph(product_code)
        except Neo4jError as exc:
            raise AppError("NEO4J_UNAVAILABLE", "Knowledge graph is unavailable", 503) from exc
        if graph is None:
            raise AppError(
                "PRODUCT_GRAPH_NOT_SYNCED",
                "Product exists but its knowledge graph has not been synchronized",
                404,
                {"information_status": "NOT_SYNCED"},
            )
        return graph
