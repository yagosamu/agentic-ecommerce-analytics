# Learning Notes

This repository is my curated portfolio version of a study project about AI data engineering for ecommerce analytics.

## Main Lessons

The biggest architectural lesson was that not every business question belongs in the same data store.

Postgres is the right tool when the answer is exact: revenue, counts, averages, rankings, joins, and distributions. Qdrant is useful when the question is about meaning: complaints, recurring themes, satisfaction, and sentiment in free-text reviews.

## Decisions I Want To Show

- I separated generated runtime data from source code.
- I kept secrets and course prompts out of the public repository.
- I reorganized the original learning structure into production-like modules.
- I used Pydantic to make the Python domain model match database constraints.
- I used named vectors in Qdrant so the local search layer is predictable.
- I exposed data access through tools so the agent can route work instead of relying on a single prompt.

## Local Issues I Solved

On Windows, Postgres running locally can conflict with the Docker Postgres port. The workaround in the scripts is to run `psql` through `docker exec`, which keeps the query path tied to the container created by Docker Compose.

The Qdrant ingestion is implemented directly with `qdrant-client` so the collection uses the vector name expected by the local semantic search flow.

## What Is Intentionally Excluded

- Course prompts.
- Private assistant configuration.
- Generated review datasets.
- `.env` files and ShadowTraffic license values.
- Virtual environments and Python cache files.
