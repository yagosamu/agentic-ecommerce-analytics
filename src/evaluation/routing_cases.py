from collections import Counter
from dataclasses import dataclass
from typing import Literal


RoutingKind = Literal["sql", "memory", "hybrid"]


@dataclass(frozen=True)
class RoutingCase:
    name: str
    kind: RoutingKind
    question: str
    expected_tools: tuple[str, ...]
    expected_answer_hint: str


def build_routing_cases() -> list[RoutingCase]:
    return [
        RoutingCase(
            name="revenue-by-state",
            kind="sql",
            question="Qual o faturamento total por estado?",
            expected_tools=("run_ledger_query",),
            expected_answer_hint="Tabela com receita agregada por UF.",
        ),
        RoutingCase(
            name="payment-distribution",
            kind="sql",
            question="Qual a distribuicao de pedidos por forma de pagamento?",
            expected_tools=("run_ledger_query",),
            expected_answer_hint="Contagem e percentual por pix, boleto e cartao.",
        ),
        RoutingCase(
            name="delivery-complaints",
            kind="memory",
            question="Quais sao as principais reclamacoes sobre entrega?",
            expected_tools=("search_customer_memory",),
            expected_answer_hint="Temas de atraso, frete, rastreamento ou produto danificado.",
        ),
        RoutingCase(
            name="product-quality-voice",
            kind="memory",
            question="O que os clientes dizem sobre qualidade dos produtos?",
            expected_tools=("search_customer_memory",),
            expected_answer_hint="Padroes positivos e negativos nas reviews.",
        ),
        RoutingCase(
            name="regional-satisfaction-impact",
            kind="hybrid",
            question="Analise satisfacao por regiao com impacto financeiro.",
            expected_tools=("run_ledger_query", "search_customer_memory"),
            expected_answer_hint="Cruza faturamento regional com temas de reviews.",
        ),
    ]


def summarize_expected_tools(cases: list[RoutingCase]) -> dict[str, int]:
    return dict(Counter(case.kind for case in cases))
