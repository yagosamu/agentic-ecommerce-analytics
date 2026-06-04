"""
The Memory — Semantic search over reviews in Qdrant.
Demonstrates RAG: same query finds semantically similar reviews
even when exact words differ ("demorou 15 dias" = "nao recebi" = "entrega atrasada").
"""
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "shopagent_reviews")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

QUERIES = [
    "Clientes reclamando de entrega atrasada",
    "Reviews positivos sobre qualidade do produto",
    "Problemas com pagamento ou frete caro",
]


def build_query_engine():
    Settings.embed_model = FastEmbedEmbedding(model_name=EMBED_MODEL)
    Settings.llm = None

    client = QdrantClient(url=QDRANT_URL)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION)
    index = VectorStoreIndex.from_vector_store(vector_store)
    return index.as_retriever(similarity_top_k=TOP_K)


def run_search(retriever, query: str) -> None:
    print(f"\n{'='*60}")
    print(f"QUERY: \"{query}\"")
    print(f"{'='*60}")

    nodes = retriever.retrieve(query)

    for i, node in enumerate(nodes, 1):
        score = node.score or 0.0
        meta = node.metadata
        comment = node.text
        print(f"\n  [{i}] score={score:.4f} | rating={meta.get('rating')}/5 | sentiment={meta.get('sentiment')}")
        print(f"      \"{comment}\"")
        print(f"      order_id: {meta.get('order_id', '')[:8]}...")


def main() -> None:
    print("=== The Memory — Semantic Search Demo ===")
    print(f"Collection: {COLLECTION} | Model: {EMBED_MODEL} | top_k={TOP_K}\n")

    retriever = build_query_engine()

    for query in QUERIES:
        run_search(retriever, query)

    print(f"\n{'='*60}")
    print("KEY INSIGHT: SQL searches for exact words.")
    print("Qdrant searches for MEANING.")
    print("'demorou 15 dias', 'nao recebi', 'entrega atrasada'")
    print("-> all found by the same query, zero shared keywords.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
