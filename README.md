# Agentic Ecommerce Analytics

An AI data engineering project that combines structured analytics, vector search, and an autonomous agent interface for ecommerce questions.

## Architecture

```text
+------------------+     +------------------+     +------------------+
|  DATA GENERATION |     |   AI / LLM       |     |   INTERFACE      |
|  ShadowTraffic   |     |   Claude         |     |   Chainlit       |
+--------+---------+     |   LlamaIndex     |     +--------+---------+
         |               |   LangChain      |              |
         v               |   CrewAI         |              v
+------------------+     +--------+---------+     +------------------+
|  STORAGE         |              |               |   QUALITY        |
|  Postgres        |              v               |   DeepEval       |
|  (The Ledger)    |     +------------------+     |   LangFuse       |
|  Qdrant          |<--->|   MCP Protocol   |     +------------------+
|  (The Memory)    |     +------------------+
+------------------+
```

The system uses two complementary data stores:

- **Ledger:** Postgres for exact business metrics such as revenue, orders, products, payment methods, and customer segments.
- **Memory:** Qdrant for semantic search over customer reviews, complaints, sentiment, and recurring experience themes.

## What It Does

- Generates synthetic ecommerce data with ShadowTraffic.
- Stores customers, products, and orders in Postgres.
- Writes customer reviews as JSONL files.
- Validates ecommerce entities with Pydantic models.
- Runs business queries against the relational store.
- Embeds review comments with FastEmbed and indexes them in Qdrant.
- Exposes two LangChain tools: one for SQL analytics and one for semantic review search.
- Uses a ShopAgent to route questions to the right tool.
- Adds a CrewAI workflow with separate revenue analysis, customer voice research, and executive synthesis roles.
- Includes routing evaluation cases for SQL-only, semantic-only, and hybrid questions.
- Provides a Chainlit chat interface for interactive exploration.

## Tech Stack Highlights

This project was designed to demonstrate practical AI Engineer skills beyond a basic chatbot.

| Tool | How it is used | Why it matters |
|------|----------------|----------------|
| **LangChain / LangGraph** | Builds the ShopAgent, defines tool-calling behavior, manages agent execution, and keeps conversation state with thread-based memory. | Shows agent orchestration, tool use, state management, and production-oriented LLM application patterns. |
| **Tool Selection** | The agent chooses between SQL analytics and semantic search based on the user question. Numeric questions go to the Ledger, qualitative questions go to Memory, and hybrid questions can use both. | Demonstrates routing logic, tool design, prompt/tool descriptions, and controlled access to external systems. |
| **CrewAI** | Adds a multi-agent workflow with a Revenue Analyst, Customer Voice Researcher, and Executive Advisor. | Shows how to decompose complex AI tasks into specialized agents with clear responsibilities. |
| **Docker Compose** | Runs Postgres, Qdrant, and ShadowTraffic locally as a reproducible data platform. | Demonstrates infrastructure literacy, local development environments, and service orchestration. |
| **Postgres** | Stores structured ecommerce entities and supports exact business queries. | Covers relational modeling, SQL analytics, joins, aggregations, and deterministic data access. |
| **Qdrant** | Stores embedded review comments for semantic search over customer feedback. | Demonstrates vector databases, retrieval, similarity search, and RAG-style architecture. |
| **FastEmbed** | Generates local embeddings for customer reviews before indexing them in Qdrant. | Keeps semantic search reproducible without depending on an external embedding API. |
| **Pydantic** | Defines typed ecommerce domain models and validation constraints. | Shows schema validation, data contracts, and safer structured outputs. |
| **DeepEval / pytest** | Validates routing cases for SQL-only, memory-only, and hybrid questions. | Adds evaluation discipline to agent behavior instead of relying only on manual testing. |
| **Chainlit** | Provides a chat interface for interacting with the analytics agent. | Demonstrates an end-user surface for LLM applications. |

## AI Engineering Patterns

- **Dual-store architecture:** Postgres handles exact metrics, while Qdrant handles meaning and customer sentiment.
- **Tool-aware agents:** tools are intentionally described so the LLM can choose the correct data source.
- **Hybrid retrieval:** complex questions can combine SQL results with semantic review evidence.
- **Multi-agent decomposition:** CrewAI separates quantitative analysis, qualitative research, and executive synthesis.
- **Evaluation-first mindset:** routing behavior is represented as test cases so the agent can be evaluated systematically.
- **Local-first infrastructure:** Docker Compose makes the stack reproducible without relying on external managed services.

## Demo

A simple frontend mockup to visualize the agentic ecommerce analytics workflow.

![Agentic Ecommerce Analytics dashboard](docs/assets/dashboard-screenshot.png)

## Project Structure

```text
infra/
  docker-compose.yml        Local Postgres, Qdrant, and ShadowTraffic
  init.sql                  Ecommerce relational schema
  shadowtraffic.json        Synthetic data generation config
  license.env.example       ShadowTraffic license template

src/
  domain/                   Pydantic domain models and validation demo
  analysis/                 Structured LLM analysis and SQL business queries
  retrieval/                Review ingestion and semantic search
  agent/                    LangChain tools and ShopAgent factory
  crew/                     CrewAI multi-agent report workflow
  evaluation/               Routing evaluation cases and DeepEval runner
  demos/                    Architecture comparison scripts
  app/                      Chainlit interface

frontend/
  index.html                Static dashboard mockup

docs/
  architecture.md           System design and data flow
  learning-notes.md         Personal implementation notes
  multi-agent-design.md     Crew design and evaluation notes
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create local environment files:

```bash
copy .env.example .env
copy infra\license.env.example infra\license.env
```

Fill in:

- `ANTHROPIC_API_KEY` in `.env`
- ShadowTraffic license fields in `infra/license.env`

Start local services and generate data:

```bash
cd infra
docker compose up
```

The generated reviews are written to `infra/data/reviews/`. This directory is ignored by Git.

## Common Commands

From the project root:

```bash
python src/domain/validation_demo.py
python src/analysis/ledger_queries.py
python src/retrieval/ingest_reviews.py
python src/retrieval/semantic_search.py
python src/agent/shopagent.py
python src/crew/ecommerce_intelligence_crew.py
python src/demos/compare_single_agent_vs_crew.py
python -m pytest tests
chainlit run src/app/chainlit_app.py --port 8000
```

Run optional DeepEval routing checks:

```bash
python src/evaluation/deepeval_routing.py
```

If Docker Compose creates a different Postgres container name, override it:

```bash
set SHOPAGENT_POSTGRES_CONTAINER=infra-postgres-1
```
