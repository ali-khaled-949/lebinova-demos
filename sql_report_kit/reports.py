"""Daily sales reporting on SQLite: schema, an indexed report query, and a plan check.

The same SQL pattern (date-bucketed totals with a covering index) is what the SQL Server reports use.
"""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    sold_at TEXT NOT NULL,          -- ISO date, e.g. 2026-10-01
    region TEXT NOT NULL,
    amount_cents INTEGER NOT NULL
);
"""

DAILY_TOTALS = """
SELECT sold_at, region, COUNT(*) AS orders, SUM(amount_cents) AS total_cents
FROM sales
WHERE sold_at BETWEEN ? AND ?
GROUP BY sold_at, region
ORDER BY sold_at, region;
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def add_index(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS ix_sales_date_region ON sales (sold_at, region, amount_cents)")


def daily_totals(conn: sqlite3.Connection, start: str, end: str) -> list[tuple]:
    return conn.execute(DAILY_TOTALS, (start, end)).fetchall()


def plan(conn: sqlite3.Connection, start: str, end: str) -> str:
    rows = conn.execute("EXPLAIN QUERY PLAN " + DAILY_TOTALS, (start, end)).fetchall()
    return " | ".join(row[-1] for row in rows)
