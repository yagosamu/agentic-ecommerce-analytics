from crew.ecommerce_intelligence_crew import build_agent_specs, build_task_specs


def test_agent_specs_define_three_distinct_business_roles():
    specs = build_agent_specs()

    assert [spec.key for spec in specs] == [
        "revenue_analyst",
        "customer_voice_researcher",
        "executive_advisor",
    ]
    assert specs[0].tool_names == ("run_ledger_query",)
    assert specs[1].tool_names == ("search_customer_memory",)
    assert specs[2].tool_names == ()


def test_task_specs_keep_analysis_and_research_before_synthesis():
    specs = build_task_specs("Satisfacao por regiao com impacto financeiro")

    assert [spec.key for spec in specs] == [
        "quantitative_analysis",
        "customer_voice_research",
        "executive_synthesis",
    ]
    assert specs[2].depends_on == ("quantitative_analysis", "customer_voice_research")
    assert "Satisfacao por regiao" in specs[0].description
    assert "Satisfacao por regiao" in specs[1].description
    assert "Satisfacao por regiao" in specs[2].description
