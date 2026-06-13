import csv
import io
import os
import re
import subprocess
from collections.abc import Sequence

from fastembed import TextEmbedding
from qdrant_client import QdrantClient


READ_ONLY_PREFIXES = ("select", "with")
MUTATING_SQL = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create)\b", re.IGNORECASE)

CONTAINER = os.getenv("SHOPAGENT_POSTGRES_CONTAINER", "infra-postgres-1")
POSTGRES_USER = os.getenv("POSTGRES_USER", "shopagent")
POSTGRES_DB = os.getenv("POSTGRES_DB", "shopagent")
DB_ARGS = ["-U", POSTGRES_USER, "-d", POSTGRES_DB]

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION = os.getenv("QDRANT_COLLECTION", "shopagent_reviews")
VECTOR_NAME = "fast-all-minilm-l6-v2"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embed_model: TextEmbedding | None = None
_qdrant_client: QdrantClient | None = None


def ensure_select_query(query: str) -> str:
    cleaned = query.strip()
    lowered = cleaned.lower()
    if not lowered.startswith(READ_ONLY_PREFIXES) or MUTATING_SQL.search(cleaned):
        raise ValueError("Only read-only SELECT/CTE queries are allowed.")
    return cleaned


def format_rows_as_markdown(rows: Sequence[dict]) -> str:
    if not rows:
        return "No results."

    columns = list(rows[0].keys())
    lines = [
        " | ".join(columns),
        " | ".join("---" for _ in columns),
    ]
    for row in rows:
        lines.append(" | ".join(str(row.get(column, "")) for column in columns))
    return "\n".join(lines)


def _get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(model_name=EMBED_MODEL)
    return _embed_model


def _get_qdrant() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        kwargs: dict = {"url": QDRANT_URL}
        if QDRANT_API_KEY:
            kwargs["api_key"] = QDRANT_API_KEY
        _qdrant_client = QdrantClient(**kwargs)
    return _qdrant_client


def run_ledger_query(query: str) -> str:
    """Run a read-only SQL query against the local ecommerce Postgres ledger."""
    cleaned = ensure_select_query(query)
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER, "psql", *DB_ARGS, "-A", "--csv", "-c", cleaned],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        return f"SQL error: {exc.stderr.strip()}"

    reader = csv.DictReader(io.StringIO(result.stdout.strip()))
    return format_rows_as_markdown(list(reader))


def search_customer_memory(query: str, limit: int = 5) -> str:
    """Search review memory for customer experience themes."""
    try:
        model = _get_embed_model()
        client = _get_qdrant()
        vector = list(model.embed([query]))[0].tolist()
        points = client.query_points(
            collection_name=COLLECTION,
            query=vector,
            using=VECTOR_NAME,
            limit=limit,
        ).points
    except Exception as exc:
        return f"Qdrant search error: {exc}"

    if not points:
        return "No reviews found."

    lines = []
    for point in points:
        payload = point.payload or {}
        lines.append(
            f"score={point.score:.3f} | rating={payload.get('rating')}/5 | "
            f"sentiment={payload.get('sentiment')}\n"
            f"  \"{payload.get('document')}\""
        )
    return "\n\n".join(lines)


try:
    from crewai.tools import tool

    ledger_tool = tool("run_ledger_query")(run_ledger_query)
    memory_tool = tool("search_customer_memory")(search_customer_memory)
except ImportError:
    ledger_tool = run_ledger_query
    memory_tool = search_customer_memory
