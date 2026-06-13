def build_comparison_table() -> list[dict[str, str]]:
    return [
        {
            "dimension": "Routing",
            "single_agent": "One agent decides every tool call during one reasoning loop.",
            "multi_agent_crew": "Specialized agents split quantitative, qualitative, and synthesis work.",
        },
        {
            "dimension": "Evidence",
            "single_agent": "Can mix SQL and review evidence, but the chain is harder to audit.",
            "multi_agent_crew": "Each task produces a focused artifact before final synthesis.",
        },
        {
            "dimension": "Output",
            "single_agent": "Best for quick interactive answers.",
            "multi_agent_crew": "Best for executive reports and multi-step business analysis.",
        },
    ]


def print_comparison() -> None:
    print("Single Agent vs Multi-Agent Crew\n")
    for row in build_comparison_table():
        print(f"## {row['dimension']}")
        print(f"- Single agent: {row['single_agent']}")
        print(f"- Crew: {row['multi_agent_crew']}\n")


if __name__ == "__main__":
    print_comparison()
