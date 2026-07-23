import hashlib
import uuid
from typing import Any

from sqlalchemy import bindparam, text
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

    def get_food_preferences(self, user_id: int) -> dict[str, list[str]]:
        items = self.list_for_user(user_id)
        return {
            "exclude_ingredients": [item["name"] for item in items if item["is_enabled"] and item["preference_type"] == "EXCLUDE"],
            "preferred_ingredients": [item["name"] for item in items if item["is_enabled"] and item["preference_type"] == "PREFER"],
        }

    def replace_food_preferences(
        self,
        user_id: int,
        exclude_ingredients: list[str],
        preferred_ingredients: list[str],
    ) -> dict[str, list[str]]:
        names = list(dict.fromkeys(exclude_ingredients + preferred_ingredients))
        with self._factory.begin() as session:
            existing_rows = session.execute(text("""
                SELECT ingredient_name,ingredient_code FROM user_ingredient_preference
                WHERE user_id=:user_id
            """), {"user_id": user_id}).mappings().all()
            code_by_name = {row["ingredient_name"]: row["ingredient_code"] for row in existing_rows}
            if names:
                snapshot_rows = session.execute(text("""
                    SELECT normalized_name,MIN(entity_code) AS entity_code
                    FROM product_ingredient_snapshot
                    WHERE normalized_name IN :names AND entity_type='INGREDIENT'
                    GROUP BY normalized_name
                """).bindparams(bindparam("names", expanding=True)), {"names": names}).mappings().all()
                code_by_name.update({row["normalized_name"]: row["entity_code"] for row in snapshot_rows})
            session.execute(text("DELETE FROM user_ingredient_preference WHERE user_id=:user_id"), {"user_id": user_id})
            rows = []
            for preference_type, values in (("EXCLUDE", exclude_ingredients), ("PREFER", preferred_ingredients)):
                for name in values:
                    ingredient_code = code_by_name.get(name) or "USR_" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:20].upper()
                    rows.append({
                        "preference_code": "PREF" + uuid.uuid4().hex[:20].upper(),
                        "user_id": user_id,
                        "preference_type": preference_type,
                        "ingredient_code": ingredient_code,
                        "ingredient_name": name,
                        "strength": 100 if preference_type == "EXCLUDE" else 60,
                        "preference_source": "USER_INPUT",
                    })
            if rows:
                session.execute(text("""
                    INSERT INTO user_ingredient_preference
                      (preference_code,user_id,preference_type,ingredient_code,ingredient_name,
                       strength,is_enabled,preference_source)
                    VALUES (:preference_code,:user_id,:preference_type,:ingredient_code,:ingredient_name,
                            :strength,1,:preference_source)
                """), rows)
        return self.get_food_preferences(user_id)
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
