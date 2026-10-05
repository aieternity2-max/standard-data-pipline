from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from app.config.settings import settings


def get_database_engine(
    database_name: str | None = None,
):
    """
    Create a SQLAlchemy engine
    for the requested MySQL database.
    """

    if database_name is None:
        database_name = settings.mysql_database

    if not database_name:
        raise ValueError(
            "Database name is required"
        )

    if not settings.mysql_user:
        raise ValueError(
            "MYSQL_USER is not configured"
        )

    if settings.mysql_password is None:
        raise ValueError(
            "MYSQL_PASSWORD is not configured"
        )

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=settings.mysql_user,
        password=settings.mysql_password,
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=database_name,
    )

    return create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=settings.mysql_pool_size,
    max_overflow=settings.mysql_max_overflow,
    pool_timeout=settings.mysql_pool_timeout,
    pool_recycle=settings.mysql_pool_recycle,
    )