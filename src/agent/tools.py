import csv
import io
import os
import subprocess
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from langchain_core.tools import tool

CONTAINER = os.getenv("SHOPAGENT_POSTGRES_CONTAINER", "infra-postgres-1")
POSTGRES_USER = os.getenv("POSTGRES_USER", "shopagent")
POSTGRES_DB = os.getenv("POSTGRES_DB", "shopagent")
DB_ARGS = ["-U", POSTGRES_USER, "-d", POSTGRES_DB]
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "shopagent_reviews")
VECTOR_NAME = "fast-all-minilm-l6-v2"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embed_model: TextEmbedding | None = None
_qdrant_client: QdrantClient | None = None


def _get_embed_model() -> TextEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = TextEmbedding(model_name=EMBED_MODEL)
    return _embed_model


def _get_qdrant() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=QDRANT_URL)
    return _qdrant_client


@tool
def supabase_execute_sql(sql: str) -> str:
    """Use for exact data: revenue, counts, averages, orders, products, customers.
    Input must be a valid SQL query string.
    Available tables:
      customers(customer_id, name, email, city, state, segment)
      products(product_id, name, category, price, brand)
      orders(order_id, customer_id, product_id, qty, total, status, payment, created_at)
    Enum values — status: delivered|shipped|processing|cancelled
                   segment: premium|standard|basic
                   payment: pix|credit_card|boleto
    """
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER, "psql", *DB_ARGS, "-A", "--csv", "-c", sql],
            capture_output=True, text=True, check=True,
        )
        reader = csv.DictReader(io.StringIO(result.stdout.strip()))
        rows = list(reader)
        return "\n".join(str(r) for r in rows) if rows else "No results."
    except subprocess.CalledProcessError as e:
        return f"SQL error: {e.stderr.strip()}"


@tool
def qdrant_semantic_search(query: str) -> str:
    """Use for meaning: complaints, sentiment, review themes, customer opinions.
    Input must be a natural language description of what to search.
    Returns the most similar customer reviews with similarity score, rating and sentiment.
    """
    model = _get_embed_model()
    client = _get_qdrant()
    vectors = list(model.embed([query]))
    results = client.query_points(
        collection_name=COLLECTION,
        query=vectors[0].tolist(),
        using=VECTOR_NAME,
        limit=5,
    ).points
    if not results:
        return "No reviews found."
    lines = []
    for r in results:
        p = r.payload
        lines.append(
            f"score={r.score:.3f} | rating={p.get('rating')}/5 | sentiment={p.get('sentiment')}\n"
            f"  \"{p.get('document')}\""
        )
    return "\n\n".join(lines)


TOOLS = [supabase_execute_sql, qdrant_semantic_search]
