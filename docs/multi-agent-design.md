# Multi-Agent Design

The single-agent interface is useful for quick analytics questions. For broader questions, such as regional satisfaction with financial impact, I added a CrewAI workflow that separates the work into three responsibilities.

## Roles

| Role | Responsibility | Tool access |
| --- | --- | --- |
| Revenue Analyst | Query exact revenue, order, product, payment, segment, and regional metrics | `run_ledger_query` |
| Customer Voice Researcher | Find themes and examples in customer reviews | `search_customer_memory` |
| Executive Advisor | Combine the evidence into a concise action plan | No direct tools |

## Task Flow

```text
User question
    |
    +--> Quantitative analysis -> Revenue Analyst -> Postgres
    |
    +--> Customer voice research -> Customer Voice Researcher -> Qdrant
    |
    +--> Executive synthesis -> Executive Advisor -> final report
```

The executive advisor receives the outputs from the first two tasks as context. That makes the final report easier to audit because the numeric and qualitative evidence are produced separately before synthesis.

## Evaluation

The evaluation cases live in `src/evaluation/routing_cases.py`.

They intentionally cover:

- SQL-only questions.
- Memory-only questions.
- Hybrid questions.

The regular pytest suite checks that the routing matrix stays consistent. `src/evaluation/deepeval_routing.py` can run optional DeepEval checks when credentials and dependencies are available.
