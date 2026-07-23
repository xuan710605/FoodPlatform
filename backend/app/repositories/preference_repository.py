import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker


KIND_TO_TYPE = {
    "ALLERGEN": "EXCLUDE",
    "DIETARY_RESTRICTION": "EXCLUDE",
    "NUTRITION_TARGET": "PREFER",
}


class PreferenceRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.execute(text("""
                SELECT id,preference_code,
                       CASE WHEN preference_source IN ('ALLERGEN','DIETARY_RESTRICTION','NUTRITION_TARGET')
                            THEN preference_source
                            WHEN preference_type='EXCLUDE' THEN 'DIETARY_RESTRICTION'
                            ELSE 'NUTRITION_TARGET' END AS kind,
                       ingredient_code AS code,
                       ingredient_name AS name,preference_type,strength,is_enabled,created_at,updated_at
                FROM user_ingredient_preference
                WHERE user_id=:user_id ORDER BY created_at,id
            """), {"user_id": user_id}).mappings().all()
            return [dict(row) for row in rows]

    def create(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        preference_code = "PREF" + uuid.uuid4().hex[:20].upper()
        with self._factory.begin() as session:
            result = session.execute(text("""
                INSERT INTO user_ingredient_preference
                  (preference_code,user_id,preference_type,ingredient_code,ingredient_name,
                   strength,is_enabled,preference_source)
                VALUES (:preference_code,:user_id,:preference_type,:code,:name,:strength,1,:kind)
            """), {
                "preference_code": preference_code,
                "user_id": user_id,
                "preference_type": KIND_TO_TYPE[payload["kind"]],
                **payload,
            })
            preference_id = int(result.lastrowid)
        created = self.get_for_user(user_id, preference_id)
        if created is None:
            raise RuntimeError("created preference could not be loaded")
        return created

    def get_for_user(self, user_id: int, preference_id: int) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.execute(text("""
                SELECT id,preference_code,
                       CASE WHEN preference_source IN ('ALLERGEN','DIETARY_RESTRICTION','NUTRITION_TARGET')
                            THEN preference_source
                            WHEN preference_type='EXCLUDE' THEN 'DIETARY_RESTRICTION'
                            ELSE 'NUTRITION_TARGET' END AS kind,
                       ingredient_code AS code,
                       ingredient_name AS name,preference_type,strength,is_enabled,created_at,updated_at
                FROM user_ingredient_preference WHERE id=:id AND user_id=:user_id
            """), {"id": preference_id, "user_id": user_id}).mappings().first()
            return dict(row) if row else None

    def delete_for_user(self, user_id: int, preference_id: int) -> bool:
        with self._factory.begin() as session:
            result = session.execute(text("""
                DELETE FROM user_ingredient_preference WHERE id=:id AND user_id=:user_id
            """), {"id": preference_id, "user_id": user_id})
            return result.rowcount == 1
