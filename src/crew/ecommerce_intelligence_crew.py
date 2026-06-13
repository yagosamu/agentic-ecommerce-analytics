import os
from dataclasses import dataclass

from dotenv import load_dotenv

from crew.crew_tools import ledger_tool, memory_tool


load_dotenv()

DEFAULT_MODEL = os.getenv("SHOPAGENT_MODEL", "claude-sonnet-4-6")


@dataclass(frozen=True)
class AgentSpec:
    key: str
    role: str
    goal: str
    backstory: str
    tool_names: tuple[str, ...]


@dataclass(frozen=True)
class TaskSpec:
    key: str
    description: str
    expected_output: str
    agent_key: str
    depends_on: tuple[str, ...] = ()


def build_agent_specs() -> list[AgentSpec]:
    return [
        AgentSpec(
            key="revenue_analyst",
            role="Revenue Analyst",
            goal="Turn ecommerce ledger data into reliable revenue, order, and segment metrics.",
            backstory=(
                "A pragmatic data analyst who verifies every number through SQL before drawing "
                "business conclusions."
            ),
            tool_names=("run_ledger_query",),
        ),
        AgentSpec(
            key="customer_voice_researcher",
            role="Customer Voice Researcher",
            goal="Find customer experience patterns in reviews through semantic search.",
            backstory=(
                "A researcher focused on the language customers use when they describe delivery, "
                "quality, support, and price friction."
            ),
            tool_names=("search_customer_memory",),
        ),
        AgentSpec(
            key="executive_advisor",
            role="Executive Advisor",
            goal="Combine financial metrics and customer voice into prioritized action plans.",
            backstory=(
                "A business advisor who connects quantitative performance with qualitative signals "
                "and writes concise recommendations for leadership."
            ),
            tool_names=(),
        ),
    ]


def build_task_specs(question: str) -> list[TaskSpec]:
    return [
        TaskSpec(
            key="quantitative_analysis",
            description=(
                f"Answer the quantitative side of this ecommerce question: {question}\n\n"
                "Use SQL to inspect revenue, order volume, status distribution, products, "
                "payment methods, customer segments, and regional performance when relevant. "
                "Return only verified metrics with compact markdown tables."
            ),
            expected_output=(
                "A markdown analysis with precise metrics, tables, and brief interpretation. "
                "All numbers must come from SQL results."
            ),
            agent_key="revenue_analyst",
        ),
        TaskSpec(
            key="customer_voice_research",
            description=(
                f"Research the customer voice side of this ecommerce question: {question}\n\n"
                "Use semantic search to identify complaint themes, positive feedback, sentiment "
                "patterns, delivery issues, support issues, quality issues, and representative "
                "review snippets."
            ),
            expected_output=(
                "A markdown research brief with 3-5 customer themes, sentiment patterns, and "
                "representative review evidence."
            ),
            agent_key="customer_voice_researcher",
        ),
        TaskSpec(
            key="executive_synthesis",
            description=(
                f"Create an executive recommendation for: {question}\n\n"
                "Combine the quantitative analysis and customer research. Include an executive "
                "summary, key metric/customer insight connections, risks, and 3 prioritized actions."
            ),
            expected_output=(
                "An executive markdown report with summary, evidence, correlations, and a "
                "prioritized action plan."
            ),
            agent_key="executive_advisor",
            depends_on=("quantitative_analysis", "customer_voice_research"),
        ),
    ]


def create_ecommerce_intelligence_crew(question: str):
    from crewai import Agent, Crew, LLM, Process, Task

    tool_map = {
        "run_ledger_query": ledger_tool,
        "search_customer_memory": memory_tool,
    }
    agent_specs = {spec.key: spec for spec in build_agent_specs()}
    agents = {
        key: Agent(
            role=spec.role,
            goal=spec.goal,
            backstory=spec.backstory,
            tools=[tool_map[name] for name in spec.tool_names],
            llm=LLM(model=DEFAULT_MODEL),
            verbose=True,
        )
        for key, spec in agent_specs.items()
    }

    tasks: dict[str, Task] = {}
    for spec in build_task_specs(question):
        tasks[spec.key] = Task(
            description=spec.description,
            expected_output=spec.expected_output,
            agent=agents[spec.agent_key],
            context=[tasks[key] for key in spec.depends_on],
        )

    return Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=True,
    )


def run_ecommerce_intelligence_report(question: str) -> str:
    crew = create_ecommerce_intelligence_crew(question)
    return str(crew.kickoff())


if __name__ == "__main__":
    report = run_ecommerce_intelligence_report(
        "Analise satisfacao por regiao considerando faturamento, reclamacoes e plano de acao."
    )
    print(report)
