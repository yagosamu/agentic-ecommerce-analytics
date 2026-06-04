"""
RAG Ingest Pipeline — The Memory
Loads reviews from JSONL, embeds with FastEmbed, stores in Qdrant.
Uses named vectors (fast-all-minilm-l6-v2) compatible with mcp-server-qdrant.
"""
import glob
import json
import os
import uuid
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

REVIEWS_GLOB = str(
    Path(__file__).parent.parent.parent / "infra" / "data" / "reviews" / "reviews*.jsonl"
)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "shopagent_reviews")
VECTOR_NAME = "fast-all-minilm-l6-v2"   # must match mcp-server-qdrant default
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64


def load_reviews() -> list[dict]:
    reviews = []
    for path in sorted(glob.glob(REVIEWS_GLOB)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    reviews.append(json.loads(line))
    return reviews


def setup_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION in existing:
        client.delete_collection(COLLECTION)
        print(f"  Existing collection deleted.")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={VECTOR_NAME: VectorParams(size=384, distance=Distance.COSINE)},
    )
    print(f"  Collection '{COLLECTION}' created with vector '{VECTOR_NAME}' (384 dims).")


def main() -> None:
    print("=== RAG Ingest Pipeline — The Memory ===\n")

    print("1. Loading reviews...")
    reviews = load_reviews()
    print(f"   {len(reviews)} reviews loaded.\n")

    print(f"2. Loading embedding model: {EMBED_MODEL}")
    model = TextEmbedding(model_name=EMBED_MODEL)
    print("   Model ready.\n")

    print(f"3. Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL)
    print("   Connected.\n")

    print("4. Setting up collection...")
    setup_collection(client)
    print()

    print("5. Embedding and indexing (this may take a minute)...")
    texts = [r["comment"] for r in reviews]
    embeddings = list(model.embed(texts))

    points = []
    for review, vector in zip(reviews, embeddings):
        points.append(PointStruct(
            id=str(uuid.UUID(review["review_id"])),
            vector={VECTOR_NAME: vector.tolist()},
            payload={
                "document": review["comment"],
                "review_id": review["review_id"],
                "order_id":  review["order_id"],
                "rating":    review["rating"],
                "sentiment": review["sentiment"],
            },
        ))

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i:i + BATCH_SIZE]
        client.upsert(collection_name=COLLECTION, points=batch)
        pct = min(i + BATCH_SIZE, len(points))
        print(f"   {pct}/{len(points)} vectors indexed...", end="\r")

    count = client.count(COLLECTION).count
    print(f"\n\n=== DONE ===")
    print(f"Collection : {COLLECTION}")
    print(f"Vector     : {VECTOR_NAME} (384 dims)")
    print(f"Points     : {count}")
    print(f"Status     : {client.get_collection(COLLECTION).status}")


if __name__ == "__main__":
    main()
