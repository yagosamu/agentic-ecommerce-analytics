import pytest

from crew.crew_tools import ensure_select_query, format_rows_as_markdown


@pytest.mark.parametrize(
    "query",
    [
        "select * from orders",
        "  WITH revenue AS (select 1 as value) select value from revenue",
    ],
)
def test_ensure_select_query_accepts_read_only_queries(query):
    assert ensure_select_query(query) == query.strip()


@pytest.mark.parametrize(
    "query",
    [
        "delete from orders",
        "update orders set status = 'cancelled'",
        "drop table customers",
        "insert into orders values (1)",
    ],
)
def test_ensure_select_query_rejects_mutating_queries(query):
    with pytest.raises(ValueError, match="read-only"):
        ensure_select_query(query)


def test_format_rows_as_markdown_returns_table():
    rows = [
        {"state": "SP", "revenue": "1200.00"},
        {"state": "RJ", "revenue": "850.50"},
    ]

    assert format_rows_as_markdown(rows) == (
        "state | revenue\n"
        "--- | ---\n"
        "SP | 1200.00\n"
        "RJ | 850.50"
    )
