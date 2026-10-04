import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Load environment variables
load_dotenv()


# MySQL server configuration
MYSQL_HOST = os.getenv(
    "MYSQL_HOST",
    "localhost",
)

MYSQL_PORT = int(
    os.getenv(
        "MYSQL_PORT",
        "3306",
    )
)

MYSQL_USER = os.getenv(
    "MYSQL_USER",
)

MYSQL_PASSWORD = os.getenv(
    "MYSQL_PASSWORD",
)


# Validate common MySQL configuration
if not MYSQL_USER:
    raise ValueError(
        "MYSQL_USER is not configured"
    )

if MYSQL_PASSWORD is None:
    raise ValueError(
        "MYSQL_PASSWORD is not configured"
    )


def get_database_engine(
    database_name: str,
):
    """
    Create a SQLAlchemy engine
    for the requested MySQL database.
    """

    if not database_name:
        raise ValueError(
            "Database name is required"
        )

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=database_name,
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )