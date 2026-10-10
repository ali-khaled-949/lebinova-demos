import unittest

from reports import add_index, connect, daily_totals, plan


def seed(conn):
    rows = [
        ("2026-10-01", "west", 10000),
        ("2026-10-01", "west", 2500),
        ("2026-10-01", "east", 7000),
        ("2026-10-02", "west", 4000),
    ]
    conn.executemany("INSERT INTO sales (sold_at, region, amount_cents) VALUES (?, ?, ?)", rows)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        seed(self.conn)

    def test_daily_totals_group_by_day_and_region(self):
        result = daily_totals(self.conn, "2026-10-01", "2026-10-02")
        self.assertEqual(
            result,
            [
                ("2026-10-01", "east", 1, 7000),
                ("2026-10-01", "west", 2, 12500),
                ("2026-10-02", "west", 1, 4000),
            ],
        )

    def test_index_is_used_after_creation(self):
        add_index(self.conn)
        self.assertIn("ix_sales_date_region", plan(self.conn, "2026-10-01", "2026-10-02"))


if __name__ == "__main__":
    unittest.main()
