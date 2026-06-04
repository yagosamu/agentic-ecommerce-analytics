"""
The Ledger — Postgres business queries for ShopAgent.

Runs queries via docker exec (works around Windows/Docker Desktop auth quirks).
In production (Supabase) or Linux, swap run_query() to use psycopg2 directly.
"""
import json
import os
import subprocess


CONTAINER = os.getenv("SHOPAGENT_POSTGRES_CONTAINER", "infra-postgres-1")
POSTGRES_USER = os.getenv("POSTGRES_USER", "shopagent")
POSTGRES_DB = os.getenv("POSTGRES_DB", "shopagent")
DB_ARGS = ["-U", POSTGRES_USER, "-d", POSTGRES_DB]


def run_query(sql: str) -> list[dict]:
    """Execute SQL and return rows as list of dicts via docker exec."""
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "psql", *DB_ARGS, "--tuples-only", "-A",
         "--csv", "-c", sql],
        capture_output=True, text=True, check=True,
    )
    lines = result.stdout.strip().splitlines()
    if not lines:
        return []
    headers = lines[0].split(",")
    rows = []
    for line in lines[1:]:
        values = line.split(",")
        rows.append(dict(zip(headers, values)))
    return rows


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("  (sem resultados)")
        return
    keys = list(rows[0].keys())
    widths = {k: max(len(k), max(len(r.get(k, "")) for r in rows)) for k in keys}
    header = " | ".join(k.ljust(widths[k]) for k in keys)
    sep = "-+-".join("-" * widths[k] for k in keys)
    print(f"  {header}")
    print(f"  {sep}")
    for row in rows:
        print("  " + " | ".join(row.get(k, "").ljust(widths[k]) for k in keys))


def revenue_by_state() -> list[dict]:
    return run_query("""
        SELECT c.state,
               COUNT(DISTINCT c.customer_id) AS customers,
               COUNT(o.order_id)             AS orders,
               ROUND(SUM(o.total)::numeric,2) AS revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.state
        ORDER BY revenue DESC
        LIMIT 5
    """)


def order_status_distribution() -> list[dict]:
    return run_query("""
        SELECT status,
               COUNT(*) AS total,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),1) AS pct
        FROM orders
        GROUP BY status
        ORDER BY total DESC
    """)


def top_products_by_revenue() -> list[dict]:
    return run_query("""
        SELECT p.name,
               p.category,
               ROUND(p.price::numeric,2)      AS unit_price,
               COUNT(o.order_id)              AS orders,
               ROUND(SUM(o.total)::numeric,2) AS revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.name, p.category, p.price
        ORDER BY revenue DESC
        LIMIT 10
    """)


def payment_distribution() -> list[dict]:
    return run_query("""
        SELECT payment,
               COUNT(*)                                           AS total,
               ROUND(SUM(total)::numeric,2)                      AS revenue,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),1)      AS pct
        FROM orders
        GROUP BY payment
        ORDER BY total DESC
    """)


def segment_analysis() -> list[dict]:
    return run_query("""
        SELECT c.segment,
               COUNT(DISTINCT c.customer_id)   AS customers,
               COUNT(o.order_id)               AS orders,
               ROUND(AVG(o.total)::numeric,2)  AS avg_ticket,
               ROUND(SUM(o.total)::numeric,2)  AS revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.segment
        ORDER BY revenue DESC
    """)


def main() -> None:
    print("\n=== 1. REVENUE BY STATE (TOP 5) ===")
    print_table(revenue_by_state())

    print("\n=== 2. ORDER STATUS DISTRIBUTION ===")
    print_table(order_status_distribution())

    print("\n=== 3. TOP 10 PRODUCTS BY REVENUE ===")
    print_table(top_products_by_revenue())

    print("\n=== 4. PAYMENT METHOD DISTRIBUTION ===")
    print_table(payment_distribution())

    print("\n=== 5. CUSTOMER SEGMENT ANALYSIS ===")
    print_table(segment_analysis())


if __name__ == "__main__":
    main()
