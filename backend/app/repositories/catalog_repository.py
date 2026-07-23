from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker


class CatalogRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    def list_categories(self) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.execute(text("""
                SELECT c.category_code,c.category_name AS name,p.category_code AS parent_code,
                       c.category_level AS level,c.sort_order
                FROM category c LEFT JOIN category p ON p.id=c.parent_id
                WHERE c.status='ACTIVE' ORDER BY c.sort_order,c.id
            """)).mappings().all()
            return [dict(row) for row in rows]

    def list_brands(self) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.execute(text("""
                SELECT brand_code,brand_name AS name,logo_url,description
                FROM brand WHERE status='ACTIVE' ORDER BY brand_name,id
            """)).mappings().all()
            return [dict(row) for row in rows]
