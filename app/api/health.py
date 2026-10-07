from fastapi import APIRouter

from app.storage.sql_storage import SQLStorage
from app.storage.vector_storage import VectorStorage


router = APIRouter()


@router.get("/health")
def health_check():
    health = {
        "status": "healthy",
        "service": "Standard Data Pipeline",
        "database": "unknown",
        "vector_store": "unknown",
    }

    # Check MySQL
    try:
        sql_storage = SQLStorage()

        if sql_storage.test_connection():
            health["database"] = "healthy"
        else:
            health["database"] = "unhealthy"

    except Exception:
        health["database"] = "unhealthy"

    # Check ChromaDB
    try:
        VectorStorage()

        health["vector_store"] = "healthy"

    except Exception:
        health["vector_store"] = "unhealthy"

    # Overall status
    if (
        health["database"] != "healthy"
        or health["vector_store"] != "healthy"
    ):
        health["status"] = "unhealthy"

    return health