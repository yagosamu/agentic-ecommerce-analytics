from evaluation.routing_cases import build_routing_cases, summarize_expected_tools


def test_routing_cases_cover_sql_memory_and_hybrid_questions():
    cases = build_routing_cases()

    assert [case.kind for case in cases] == ["sql", "sql", "memory", "memory", "hybrid"]
    assert cases[0].expected_tools == ("run_ledger_query",)
    assert cases[2].expected_tools == ("search_customer_memory",)
    assert cases[-1].expected_tools == ("run_ledger_query", "search_customer_memory")


def test_summarize_expected_tools_groups_cases_by_kind():
    summary = summarize_expected_tools(build_routing_cases())

    assert summary == {
        "sql": 2,
        "memory": 2,
        "hybrid": 1,
    }
