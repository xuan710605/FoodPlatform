import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker


ROLE_ALIASES = {"PLATFORM_ADMIN": "ADMIN"}


class UserRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    def find_for_login(self, username_or_email: str) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.execute(text("""
                SELECT id,user_code,username,email,password_hash,user_type,status,created_at
                FROM sys_user
                WHERE (username=:identity OR email=:identity) AND is_deleted=0
            """), {"identity": username_or_email}).mappings().first()
            return self._with_roles(session, row)

    def get_identity(self, user_id: int) -> dict[str, Any] | None:
        with self._factory() as session:
            row = session.execute(text("""
                SELECT id,user_code,username,email,user_type,status,created_at
                FROM sys_user WHERE id=:id AND is_deleted=0
            """), {"id": user_id}).mappings().first()
            return self._with_roles(session, row)

    def username_exists(self, username: str) -> bool:
        return self._exists("username", username)

    def email_exists(self, email: str) -> bool:
        return self._exists("email", email)

    def _exists(self, column: str, value: str) -> bool:
        if column not in {"username", "email"}:
            raise ValueError("unsupported user lookup column")
        with self._factory() as session:
            return session.execute(
                text(f"SELECT 1 FROM sys_user WHERE {column}=:value AND is_deleted=0"),
                {"value": value},
            ).first() is not None

    def create_consumer(self, username: str, email: str, password_hash: str, nickname: str) -> dict[str, Any]:
        user_code = "USR" + uuid.uuid4().hex[:20].upper()
        with self._factory.begin() as session:
            role_id = session.execute(text("""
                SELECT id FROM sys_role WHERE role_code='CONSUMER' AND status='ACTIVE'
            """)).scalar_one_or_none()
            if role_id is None:
                raise RuntimeError("CONSUMER role is not configured")
            try:
                result = session.execute(text("""
                    INSERT INTO sys_user
                      (user_code,username,password_hash,email,user_type,status,password_changed_at)
                    VALUES (:code,:username,:password_hash,:email,'CONSUMER','ACTIVE',CURRENT_TIMESTAMP(3))
                """), {"code": user_code, "username": username, "password_hash": password_hash, "email": email})
                user_id = int(result.lastrowid)
                session.execute(text("""
                    INSERT INTO sys_user_role (user_id,role_id,granted_by) VALUES (:user_id,:role_id,NULL)
                """), {"user_id": user_id, "role_id": role_id})
                session.execute(text("""
                    INSERT INTO user_profile (user_id,nickname) VALUES (:user_id,:nickname)
                """), {"user_id": user_id, "nickname": nickname})
            except IntegrityError:
                raise
        identity = self.get_identity(user_id)
        if identity is None:
            raise RuntimeError("created user could not be loaded")
        return identity

    def record_login(self, user_id: int) -> None:
        with self._factory.begin() as session:
            session.execute(
                text("UPDATE sys_user SET last_login_at=CURRENT_TIMESTAMP(3) WHERE id=:id"),
                {"id": user_id},
            )

    @staticmethod
    def _with_roles(session: Session, row: Any) -> dict[str, Any] | None:
        if row is None:
            return None
        result = dict(row)
        roles = session.execute(text("""
            SELECT r.role_code FROM sys_user_role ur
            JOIN sys_role r ON r.id=ur.role_id AND r.status='ACTIVE'
            WHERE ur.user_id=:user_id AND (ur.expires_at IS NULL OR ur.expires_at>CURRENT_TIMESTAMP(3))
            ORDER BY r.id
        """), {"user_id": result["id"]}).scalars().all()
        normalized = [ROLE_ALIASES.get(role, role) for role in roles]
        if not normalized and result.get("user_type"):
            normalized = [ROLE_ALIASES.get(result["user_type"], result["user_type"])]
        result["roles"] = normalized
        return result
