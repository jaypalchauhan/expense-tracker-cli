import pytest

from expense_tracker.cli import main


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "cli.db")


def run(db_path, *args):
    return main(["--db", db_path, *args])


def test_add_and_list(db_path, capsys):
    assert run(db_path, "add", "150", "food", "-n", "dinner", "-d", "2026-06-01") == 0
    assert run(db_path, "list") == 0

    out = capsys.readouterr().out
    assert "dinner" in out
    assert "150.00" in out


def test_summary_shows_percentages(db_path, capsys):
    run(db_path, "add", "300", "food", "-d", "2026-06-01")
    run(db_path, "add", "700", "rent", "-d", "2026-06-01")
    run(db_path, "summary")

    out = capsys.readouterr().out
    assert "70.0%" in out
    assert "30.0%" in out


def test_delete_missing_id_fails(db_path, capsys):
    assert run(db_path, "delete", "99") == 1
    assert "No expense with id 99" in capsys.readouterr().err


def test_invalid_date_is_rejected(db_path):
    with pytest.raises(SystemExit):
        run(db_path, "add", "100", "food", "-d", "01-06-2026")


def test_export(db_path, tmp_path, capsys):
    run(db_path, "add", "100", "food")
    out_file = tmp_path / "expenses.csv"

    assert run(db_path, "export", str(out_file)) == 0
    assert out_file.exists()
    assert "Exported 1 expenses" in capsys.readouterr().out
