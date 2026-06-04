import json
import glob
import os
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent.parent / ".env")

REVIEWS_GLOB = str(
    Path(__file__).parent.parent.parent / "infra" / "data" / "reviews" / "reviews*.jsonl"
)


class SentimentDistribution(BaseModel):
    positive: int
    neutral: int
    negative: int


class ReviewAnalysis(BaseModel):
    total_reviews: int
    average_rating: float
    sentiment_distribution: SentimentDistribution
    top_complaints: list[str]
    top_praises: list[str]


def load_reviews(n: int = 10) -> list[dict]:
    """Load n reviews balanced across sentiments (positive/neutral/negative)."""
    buckets: dict[str, list[dict]] = {"positive": [], "neutral": [], "negative": []}
    per_bucket = n // 3
    remainder = n % 3

    for path in sorted(glob.glob(REVIEWS_GLOB)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                review = json.loads(line)
                sentiment = review.get("sentiment", "neutral")
                bucket = buckets.get(sentiment, buckets["neutral"])
                if len(bucket) < per_bucket + (1 if sentiment == "positive" and remainder > 0 else 0):
                    bucket.append(review)
        if all(len(b) >= per_bucket for b in buckets.values()):
            break

    result = buckets["positive"][:per_bucket + remainder] + buckets["neutral"][:per_bucket] + buckets["negative"][:per_bucket]
    return result[:n]


def main() -> None:
    reviews = load_reviews(10)
    print(f"Reviews carregadas: {len(reviews)}\n")

    reviews_text = "\n".join(
        f"- Rating: {r['rating']}/5 | Sentiment: {r['sentiment']} | Comment: {r['comment']}"
        for r in reviews
    )

    client = Anthropic()

    response = client.messages.parse(
        model=os.getenv("SHOPAGENT_ANALYSIS_MODEL", os.getenv("SHOPAGENT_MODEL", "claude-sonnet-4-6")),
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                "Analyze these e-commerce reviews and return a structured analysis.\n\n"
                f"Reviews:\n{reviews_text}"
            ),
        }],
        output_format=ReviewAnalysis,
    )

    analysis: ReviewAnalysis = response.parsed_output

    print("=== REVIEW ANALYSIS ===")
    print(f"Total reviews:   {analysis.total_reviews}")
    print(f"Average rating:  {analysis.average_rating:.1f}/5")
    print(f"\nSentiment distribution:")
    print(f"  Positive: {analysis.sentiment_distribution.positive}")
    print(f"  Neutral:  {analysis.sentiment_distribution.neutral}")
    print(f"  Negative: {analysis.sentiment_distribution.negative}")
    print(f"\nTop complaints:")
    for complaint in analysis.top_complaints:
        print(f"  - {complaint}")
    print(f"\nTop praises:")
    for praise in analysis.top_praises:
        print(f"  - {praise}")


if __name__ == "__main__":
    main()
