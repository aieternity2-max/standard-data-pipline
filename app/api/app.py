"""FastAPI Backend Application for InsightSphere Data Pipeline."""

from __future__ import annotations

import tempfile
import traceback
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config.settings import settings
from app.loaders.loader_factory import LoaderFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.rag.rag_service import RAGService
from app.search.search_service import SearchService
from app.storage.sql_storage import SQLStorage
from app.storage.vector_storage import VectorStorage
from app.ui.services.dashboard_service import DashboardService

app = FastAPI(
    title="InsightSphere Data Pipeline API",
    description="REST API for the standard data ingestion pipeline, semantic search, AI assistant, and analytics dashboards.",
    version="1.0.0",
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Request Models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5


class RAGRequest(BaseModel):
    query: str
    n_results: int = 5


class BatchDeleteRequest(BaseModel):
    ids: list[str]


# ---------------------------------------------------------------------------
# Health & Overview Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def get_health() -> dict[str, Any]:
    """Check MySQL, ChromaDB, and general service health."""
    health: dict[str, Any] = {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "mysql": {"status": "unavailable", "details": None},
        "chromadb": {"status": "unavailable", "count": 0, "details": None},
    }

    # Check MySQL
    try:
        sql_storage = SQLStorage()
        if sql_storage.test_connection():
            health["mysql"]["status"] = "connected"
        else:
            health["mysql"]["status"] = "disconnected"
    except Exception as exc:
        health["mysql"]["details"] = str(exc)

    # Check ChromaDB
    try:
        vector_storage = VectorStorage()
        count = vector_storage.count()
        health["chromadb"]["status"] = "ready"
        health["chromadb"]["count"] = count
    except Exception as exc:
        health["chromadb"]["details"] = str(exc)

    if (
        health["mysql"]["status"] != "connected"
        or health["chromadb"]["status"] != "ready"
    ):
        health["status"] = "degraded"

    return health


@app.get("/api/overview")
def get_overview() -> dict[str, Any]:
    """Get high-level system overview stats for the dashboard."""
    doc_count = 0
    mysql_connected = False

    try:
        vector_storage = VectorStorage()
        doc_count = vector_storage.count()
    except Exception:
        pass

    try:
        sql_storage = SQLStorage()
        mysql_connected = sql_storage.test_connection()
    except Exception:
        pass

    return {
        "document_count": doc_count,
        "mysql_connected": mysql_connected,
        "ai_enabled": settings.ai_enabled,
        "embedding_provider": settings.embedding_provider,
        "llm_provider": settings.llm_provider,
        "supported_formats": [
            "csv", "xlsx", "xls", "json", "jsonl", "pdf", "docx", "txt"
        ],
        "workflow_steps": [
            {"id": "01", "name": "Upload", "desc": "Ingest structured files and docs"},
            {"id": "02", "name": "Validate", "desc": "Clean, parse, and verify schemas"},
            {"id": "03", "name": "Explore", "desc": "Browse records and vector indices"},
            {"id": "04", "name": "Ask AI", "desc": "RAG-grounded query answering"},
        ],
    }


# ---------------------------------------------------------------------------
# Upload & Ingestion Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/upload/preview")
async def preview_files(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    """Parse uploaded files using LoaderFactory and return document previews."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    all_documents = []
    file_results = []
    loading_errors = []

    with tempfile.TemporaryDirectory(prefix="insightsphere_upload_") as temp_dir:
        temp_path = Path(temp_dir)

        for index, uploaded_file in enumerate(files, start=1):
            file_name = uploaded_file.filename or f"uploaded_file_{index}"
            suffix = Path(file_name).suffix.lower()
            temp_file = temp_path / f"file_{index}{suffix}"

            content = await uploaded_file.read()
            temp_file.write_bytes(content)

            try:
                loader = LoaderFactory.get_loader(temp_file)

                if suffix == ".jsonl":
                    docs = []
                    for batch in loader.load_batches(temp_file, batch_size=1000):
                        docs.extend(batch)
                else:
                    docs = loader.load(temp_file)

                for doc in docs:
                    doc.source = file_name
                    metadata = dict(doc.metadata or {})
                    metadata["file_name"] = file_name
                    doc.metadata = metadata

                all_documents.extend(docs)

                file_results.append({
                    "file": file_name,
                    "format": suffix.upper().lstrip("."),
                    "size_bytes": len(content),
                    "status": "Loaded" if docs else "No documents produced",
                    "documents": len(docs),
                })
            except Exception as exc:
                loading_errors.append({
                    "file": file_name,
                    "error": str(exc),
                })
                file_results.append({
                    "file": file_name,
                    "format": suffix.upper().lstrip("."),
                    "size_bytes": len(content),
                    "status": "Failed to load",
                    "documents": 0,
                })

    preview_items = [
        {
            "id": doc.id,
            "source": doc.source,
            "source_type": doc.source_type,
            "content_preview": doc.content[:240] if doc.content else "",
            "metadata": doc.metadata,
        }
        for doc in all_documents[:25]
    ]

    return {
        "total_documents": len(all_documents),
        "file_results": file_results,
        "loading_errors": loading_errors,
        "preview": preview_items,
    }


@app.post("/api/upload/ingest")
async def ingest_files(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    """Ingest uploaded files through the full IngestionPipeline."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    all_documents = []
    file_results = []
    loading_errors = []

    with tempfile.TemporaryDirectory(prefix="insightsphere_ingest_") as temp_dir:
        temp_path = Path(temp_dir)

        for index, uploaded_file in enumerate(files, start=1):
            file_name = uploaded_file.filename or f"uploaded_file_{index}"
            suffix = Path(file_name).suffix.lower()
            temp_file = temp_path / f"file_{index}{suffix}"

            content = await uploaded_file.read()
            temp_file.write_bytes(content)

            try:
                loader = LoaderFactory.get_loader(temp_file)
                if suffix == ".jsonl":
                    docs = []
                    for batch in loader.load_batches(temp_file, batch_size=1000):
                        docs.extend(batch)
                else:
                    docs = loader.load(temp_file)

                for doc in docs:
                    doc.source = file_name
                    metadata = dict(doc.metadata or {})
                    metadata["file_name"] = file_name
                    doc.metadata = metadata

                all_documents.extend(docs)
                file_results.append({
                    "file": file_name,
                    "status": "Loaded",
                    "documents": len(docs),
                })
            except Exception as exc:
                loading_errors.append({"file": file_name, "error": str(exc)})
                file_results.append({"file": file_name, "status": "Failed", "documents": 0})

    if not all_documents:
        raise HTTPException(
            status_code=400,
            detail=f"Could not load documents from files. Errors: {loading_errors}",
        )

    pipeline = IngestionPipeline()
    processed_documents = pipeline.run(all_documents)

    invalid_docs = [
        {
            "id": getattr(d, "id", "unknown"),
            "source": getattr(d, "source", "unknown"),
            "source_type": getattr(d, "source_type", "unknown"),
        }
        for d in (pipeline.last_invalid_documents or [])
    ]

    quality_summary = None
    if pipeline.last_quality_summary is not None:
        qs = pipeline.last_quality_summary
        quality_summary = {
            "quality_score": qs.quality_score,
            "valid_records": qs.valid_records,
            "invalid_records": qs.invalid_records,
            "field_scores": getattr(qs, "field_scores", {}),
        }

    return {
        "input_documents": len(all_documents),
        "processed_documents": len(processed_documents),
        "sql_records": pipeline.last_sql_storage_count,
        "vector_records": pipeline.last_vector_storage_count,
        "invalid_count": len(invalid_docs),
        "invalid_documents": invalid_docs,
        "quality_summary": quality_summary,
        "ai_failures": pipeline.last_ai_failures or [],
        "file_results": file_results,
    }


# ---------------------------------------------------------------------------
# Data Explorer Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/documents")
def get_documents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    query: str | None = Query(default=None),
) -> dict[str, Any]:
    """Get paginated documents from ChromaDB with optional search filter."""
    vector_storage = VectorStorage()
    total_count = vector_storage.count()

    if query and query.strip():
        # Perform semantic search
        search_service = SearchService()
        raw_results = search_service.search(query=query.strip(), n_results=limit)
        ids = raw_results.get("ids", [[]])[0] if raw_results.get("ids") else []
        docs = raw_results.get("documents", [[]])[0] if raw_results.get("documents") else []
        metas = raw_results.get("metadatas", [[]])[0] if raw_results.get("metadatas") else []
        distances = raw_results.get("distances", [[]])[0] if raw_results.get("distances") else []

        items = []
        for i, doc_id in enumerate(ids):
            meta = metas[i] if i < len(metas) and metas[i] else {}
            content = docs[i] if i < len(docs) else ""
            dist = distances[i] if i < len(distances) else None
            items.append({
                "id": doc_id,
                "source": meta.get("source", "Unknown"),
                "source_type": meta.get("source_type", "Unknown"),
                "content": content,
                "content_preview": content[:240],
                "metadata": meta,
                "distance": dist,
            })
        return {
            "total": len(items),
            "page_size": limit,
            "offset": offset,
            "items": items,
        }

    raw = vector_storage.collection.get(
        limit=limit,
        offset=offset,
        include=["documents", "metadatas"],
    )

    ids = raw.get("ids") or []
    documents = raw.get("documents") or []
    metadatas = raw.get("metadatas") or []

    items = []
    for i, doc_id in enumerate(ids):
        meta = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
        content = documents[i] if i < len(documents) else ""
        items.append({
            "id": doc_id,
            "source": meta.get("source", "Unknown"),
            "source_type": meta.get("source_type", "Unknown"),
            "content": content,
            "content_preview": content[:240],
            "metadata": meta,
        })

    return {
        "total": total_count,
        "page_size": limit,
        "offset": offset,
        "items": items,
    }


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str) -> dict[str, Any]:
    """Delete a document chunk from ChromaDB by ID."""
    if not doc_id or not doc_id.strip():
        raise HTTPException(status_code=400, detail="Document ID is required.")

    try:
        vector_storage = VectorStorage()
        vector_storage.delete(ids=[doc_id.strip()])
        new_count = vector_storage.count()
        return {
            "success": True,
            "deleted_id": doc_id,
            "remaining_count": new_count,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {exc}",
        )


@app.post("/api/documents/batch-delete")
def batch_delete_documents(req: BatchDeleteRequest) -> dict[str, Any]:
    """Delete multiple document chunks from ChromaDB by ID list."""
    if not req.ids:
        raise HTTPException(status_code=400, detail="List of document IDs cannot be empty.")

    try:
        vector_storage = VectorStorage()
        vector_storage.delete(ids=req.ids)
        new_count = vector_storage.count()
        return {
            "success": True,
            "deleted_count": len(req.ids),
            "remaining_count": new_count,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to batch delete documents: {exc}",
        )


# ---------------------------------------------------------------------------
# Semantic Search Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/search")
def search_documents(req: SearchRequest) -> dict[str, Any]:
    """Semantic vector search over indexed documents."""
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    search_service = SearchService()
    raw = search_service.search(query=query, n_results=req.n_results)

    ids = raw.get("ids") or []
    documents = raw.get("documents") or []
    metadatas = raw.get("metadatas") or []
    distances = raw.get("distances") or []

    # Flatten nested lists if returned
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    if documents and isinstance(documents[0], list):
        documents = documents[0]
    if metadatas and isinstance(metadatas[0], list):
        metadatas = metadatas[0]
    if distances and isinstance(distances[0], list):
        distances = distances[0]

    results = []
    for i, doc_id in enumerate(ids):
        meta = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
        content = documents[i] if i < len(documents) else ""
        dist = distances[i] if i < len(distances) else None

        # Calculate a similarity percentage score (1 - distance) clamped
        similarity_score = None
        if dist is not None:
            similarity_score = max(0.0, min(1.0, 1.0 - float(dist)))

        results.append({
            "id": doc_id,
            "source": meta.get("source", "Unknown"),
            "source_type": meta.get("source_type", "Unknown"),
            "content": content,
            "preview": content[:360] + ("..." if len(content) > 360 else ""),
            "metadata": meta,
            "distance": dist,
            "similarity_score": round(similarity_score * 100, 1) if similarity_score else None,
        })

    # Collect available filter options
    available_sources = sorted({str(r["source"]) for r in results})
    available_types = sorted({str(r["source_type"]) for r in results})

    return {
        "query": query,
        "count": len(results),
        "results": results,
        "available_sources": available_sources,
        "available_types": available_types,
    }


# ---------------------------------------------------------------------------
# Ask AI (RAG Service) Endpoint
# ---------------------------------------------------------------------------

@app.post("/api/rag/ask")
def ask_ai(req: RAGRequest) -> dict[str, Any]:
    """Retrieve grounded context and generate answer via RAG."""
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        rag_service = RAGService()
        result = rag_service.answer(query=query, n_results=req.n_results)
        return {
            "query": query,
            "answer": result.get("answer", ""),
            "context": result.get("context", ""),
            "sources": result.get("sources", []),
            "result_count": result.get("result_count", 0),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Business Analytics Dashboards Endpoint
# ---------------------------------------------------------------------------

@app.get("/api/dashboards")
def get_dashboards() -> dict[str, Any]:
    """Execute business analytics and return structured data for dashboards."""
    try:
        service = DashboardService()
        data = service.analyze()

        # Clean/sanitize any NaN or Infinity values for JSON compliance
        def sanitize(obj: Any) -> Any:
            import math
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return round(obj, 4)
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            return obj

        return sanitize(data)
    except Exception as exc:
        # Fallback with informative error
        trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate analytics: {exc}\n{trace}",
        )
