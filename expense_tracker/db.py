"""SQLite storage layer for the expense tracker."""

import csv
import os
import sqlite3
from datetime import date
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".expenses.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    note TEXT DEFAULT '',
    spent_on TEXT NOT NULL
);
"""


class ExpenseDB:
    """Thin wrapper around an SQLite database of expenses."""

    def __init__(self, db_path=None):
        path = db_path or os.environ.get("EXPENSE_DB") or DEFAULT_DB_PATH
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def add(self, amount, category, note="", spent_on=None):
        """Insert an expense and return its id."""
        if amount <= 0:
            raise ValueError("amount must be greater than zero")
        spent_on = spent_on or date.today().isoformat()
        cur = self.conn.execute(
            "INSERT INTO expenses (amount, category, note, spent_on) VALUES (?, ?, ?, ?)",
            (amount, category.lower().strip(), note, spent_on),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self, month=None, category=None):
        """Return expenses, optionally filtered by month (YYYY-MM) and category."""
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        if month:
            query += " AND spent_on LIKE ?"
            params.append(f"{month}%")
        if category:
            query += " AND category = ?"
            params.append(category.lower().strip())
        query += " ORDER BY spent_on DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    def summary(self, month=None):
        """Return (category, total) pairs, highest spend first."""
        query = "SELECT category, SUM(amount) AS total FROM expenses"
        params = []
        if month:
            query += " WHERE spent_on LIKE ?"
            params.append(f"{month}%")
        query += " GROUP BY category ORDER BY total DESC"
        return self.conn.execute(query, params).fetchall()

    def delete(self, expense_id):
        """Delete an expense by id. Returns True if a row was removed."""
        cur = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def export_csv(self, out_path, month=None):
        """Write expenses to a CSV file and return the number of rows written."""
        rows = self.list(month=month)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "amount", "category", "note", "spent_on"])
            for row in rows:
                writer.writerow([row["id"], row["amount"], row["category"], row["note"], row["spent_on"]])
        return len(rows)
