import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker


ADDRESS_SELECT = """
SELECT address_code,receiver_name,receiver_phone,province,city,district,
       detail_address,postal_code,is_default,created_at,updated_at
FROM user_address
WHERE user_id=:user_id AND is_deleted=0
"""


class AddressRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows = session.execute(
                text(ADDRESS_SELECT + " ORDER BY is_default DESC,updated_at DESC,id DESC"),
                {"user_id": user_id},
            ).mappings().all()
            return [self._normalize(row) for row in rows]

    def get_for_user(self, user_id: int, address_code: str) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.execute(
                text(ADDRESS_SELECT + " AND address_code=:address_code"),
                {"user_id": user_id, "address_code": address_code},
            ).mappings().first()
            return self._normalize(row) if row else None

    def create(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        address_code = "ADDR" + uuid.uuid4().hex[:20].upper()
        with self._factory.begin() as session:
            count = session.execute(
                text("SELECT COUNT(*) FROM user_address WHERE user_id=:user_id AND is_deleted=0 FOR UPDATE"),
                {"user_id": user_id},
            ).scalar_one()
            make_default = bool(payload["is_default"] or count == 0)
            if make_default:
                self._clear_default(session, user_id)
            session.execute(
                text("""
                    INSERT INTO user_address
                      (address_code,user_id,receiver_name,receiver_phone,province,city,district,
                       detail_address,postal_code,is_default,is_deleted)
                    VALUES
                      (:address_code,:user_id,:receiver_name,:receiver_phone,:province,:city,:district,
                       :detail_address,:postal_code,:is_default,0)
                """),
                {**payload, "address_code": address_code, "user_id": user_id, "is_default": make_default},
            )
        created = self.get_for_user(user_id, address_code)
        if created is None:
            raise RuntimeError("created address could not be loaded")
        return created

    def update(self, user_id: int, address_code: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            row = session.execute(
                text("""
                    SELECT id,is_default FROM user_address
                    WHERE address_code=:address_code AND user_id=:user_id AND is_deleted=0 FOR UPDATE
                """),
                {"address_code": address_code, "user_id": user_id},
            ).mappings().first()
            if not row:
                return None
            make_default = bool(payload["is_default"])
            if make_default:
                self._clear_default(session, user_id)
            session.execute(
                text("""
                    UPDATE user_address
                    SET receiver_name=:receiver_name,receiver_phone=:receiver_phone,
                        province=:province,city=:city,district=:district,
                        detail_address=:detail_address,postal_code=:postal_code,
                        is_default=:is_default
                    WHERE id=:id
                """),
                {**payload, "id": row["id"], "is_default": make_default},
            )
            self._ensure_default(session, user_id)
        return self.get_for_user(user_id, address_code)

    def delete(self, user_id: int, address_code: str) -> bool:
        with self._factory.begin() as session:
            row = session.execute(
                text("""
                    SELECT id FROM user_address
                    WHERE address_code=:address_code AND user_id=:user_id AND is_deleted=0 FOR UPDATE
                """),
                {"address_code": address_code, "user_id": user_id},
            ).mappings().first()
            if not row:
                return False
            session.execute(
                text("""
                    UPDATE user_address
                    SET is_deleted=1,is_default=0,deleted_at=CURRENT_TIMESTAMP(3)
                    WHERE id=:id
                """),
                {"id": row["id"]},
            )
            self._ensure_default(session, user_id)
            return True

    def set_default(self, user_id: int, address_code: str) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            row = session.execute(
                text("""
                    SELECT id FROM user_address
                    WHERE address_code=:address_code AND user_id=:user_id AND is_deleted=0 FOR UPDATE
                """),
                {"address_code": address_code, "user_id": user_id},
            ).mappings().first()
            if not row:
                return None
            self._clear_default(session, user_id)
            session.execute(text("UPDATE user_address SET is_default=1 WHERE id=:id"), {"id": row["id"]})
        return self.get_for_user(user_id, address_code)

    @staticmethod
    def _clear_default(session: Session, user_id: int) -> None:
        session.execute(
            text("UPDATE user_address SET is_default=0 WHERE user_id=:user_id AND is_deleted=0"),
            {"user_id": user_id},
        )

    @staticmethod
    def _ensure_default(session: Session, user_id: int) -> None:
        has_default = session.execute(
            text("""
                SELECT 1 FROM user_address
                WHERE user_id=:user_id AND is_deleted=0 AND is_default=1 LIMIT 1
            """),
            {"user_id": user_id},
        ).first()
        if has_default:
            return
        address_id = session.execute(
            text("""
                SELECT id FROM user_address
                WHERE user_id=:user_id AND is_deleted=0
                ORDER BY updated_at DESC,id DESC LIMIT 1 FOR UPDATE
            """),
            {"user_id": user_id},
        ).scalar_one_or_none()
        if address_id is not None:
            session.execute(text("UPDATE user_address SET is_default=1 WHERE id=:id"), {"id": address_id})

    @staticmethod
    def _normalize(row: Any) -> dict[str, Any]:
        item = dict(row)
        item["is_default"] = bool(item["is_default"])
        return item
