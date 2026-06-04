# Architecture

This project is organized around a dual-store pattern for ecommerce analytics.

## Ledger

The Ledger is the relational source of truth. It uses Postgres to store entities that need exact answers:

- customers
- products
- orders

Questions such as "revenue by state", "order status distribution", and "top products by revenue" should be answered with SQL because the result needs deterministic aggregation.

## Memory

The Memory is the semantic layer. Customer reviews are stored as JSONL files, embedded with FastEmbed, and indexed in Qdrant.

This makes it possible to search by meaning instead of exact words. A query about delayed deliveries can still retrieve comments that mention lack of tracking, damaged packages, or long waiting times.

## Agent Layer

The ShopAgent exposes two tools:

- `supabase_execute_sql`: exact metrics from Postgres.
- `qdrant_semantic_search`: customer experience insights from Qdrant.

The agent decides which tool to use from the user's question. Numeric questions go to the Ledger, qualitative questions go to Memory, and hybrid questions can use both.

## Local Flow

```text
infra/shadowtraffic.json
        |
        v
ShadowTraffic
        |
        +-- customers/products/orders --> Postgres
        |
        +-- reviews JSONL -------------> infra/data/reviews
                                             |
                                             v
                                     FastEmbed embeddings
                                             |
                                             v
                                           Qdrant
```

The final application is a Chainlit chat interface backed by a LangChain/LangGraph agent.
