from demos.compare_single_agent_vs_crew import build_comparison_table


def test_comparison_table_highlights_coordination_difference():
    table = build_comparison_table()

    assert table[0]["dimension"] == "Routing"
    assert table[0]["single_agent"]
    assert table[0]["multi_agent_crew"]
    assert any(row["dimension"] == "Output" for row in table)
