from neo4j import Driver, GraphDatabase

from app.core.config import Settings


def create_neo4j_driver(settings: Settings) -> Driver:
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password.get_secret_value()),
        connection_timeout=5,
        max_connection_pool_size=20,
    )
