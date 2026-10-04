from sqlalchemy import text

from app.config.database import get_database_engine


def test_database_connection():

    engine = get_database_engine(
        "OFFICE"
    )

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        assert result.scalar() == 1