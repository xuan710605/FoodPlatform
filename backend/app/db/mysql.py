from collections.abc import Iterator
from urllib.parse import quote_plus

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def create_mysql_engine(settings: Settings) -> Engine:
    password = quote_plus(settings.mysql_password.get_secret_value())
    url = (
        f"mysql+pymysql://{quote_plus(settings.mysql_user)}:{password}"
        f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
        f"?charset={settings.mysql_charset}"
    )
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=10,
        connect_args={"connect_timeout": 5, "read_timeout": 10, "write_timeout": 10},
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
