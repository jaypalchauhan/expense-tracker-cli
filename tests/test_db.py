import pytest

from expense_tracker.db import ExpenseDB


@pytest.fixture
def db(tmp_path):
    database = ExpenseDB(tmp_path / "test.db")
    yield database
    database.close()


def test_add_returns_incrementing_ids(db):
    first = db.add(120.50, "food", "lunch", "2026-06-01")
    second = db.add(80.00, "travel", "metro", "2026-06-02")
    assert first == 1
    assert second == 2


def test_add_rejects_non_positive_amount(db):
    with pytest.raises(ValueError):
        db.add(0, "food")
    with pytest.raises(ValueError):
        db.add(-50, "food")


def test_category_is_normalised(db):
    db.add(100, "  Food ", spent_on="2026-06-01")
    rows = db.list()
    assert rows[0]["category"] == "food"


def test_list_filters_by_month_and_category(db):
    db.add(100, "food", spent_on="2026-05-15")
    db.add(200, "food", spent_on="2026-06-01")
    db.add(300, "rent", spent_on="2026-06-01")

    assert len(db.list()) == 3
    assert len(db.list(month="2026-06")) == 2
    assert len(db.list(month="2026-06", category="food")) == 1
    assert len(db.list(category="rent")) == 1


def test_summary_groups_by_category(db):
    db.add(100, "food", spent_on="2026-06-01")
    db.add(50, "food", spent_on="2026-06-02")
    db.add(500, "rent", spent_on="2026-06-01")

    totals = {row["category"]: row["total"] for row in db.summary()}
    assert totals == {"food": 150, "rent": 500}

    # highest spend should come first
    assert db.summary()[0]["category"] == "rent"


def test_delete(db):
    expense_id = db.add(100, "food")
    assert db.delete(expense_id) is True
    assert db.delete(expense_id) is False
    assert db.list() == []


def test_export_csv(db, tmp_path):
    db.add(100, "food", "lunch", "2026-06-01")
    db.add(200, "travel", "cab", "2026-06-02")
    out = tmp_path / "out.csv"

    count = db.export_csv(out)

    assert count == 2
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "id,amount,category,note,spent_on"
    assert len(lines) == 3
