# expense-tracker-cli

A fast, no-nonsense expense tracker for the terminal. Records expenses in a local
SQLite database — no accounts, no cloud, your data stays on your machine.

## Features

- Add expenses with amount, category, optional note and date
- List expenses with month/category filters and a running total
- Category-wise monthly summary with percentage breakdown
- Export to CSV for spreadsheets
- Zero dependencies — pure Python standard library

## Installation

Requires Python 3.9+. Install the latest packaged release directly:

```bash
pip install https://github.com/jaypalchauhan/expense-tracker-cli/releases/download/v1.0.0/expense_tracker_cli-1.0.0-py3-none-any.whl
```

Or from source:

```bash
git clone https://github.com/jaypalchauhan/expense-tracker-cli.git
cd expense-tracker-cli
pip install .
```

Or run it directly without installing:

```bash
python -m expense_tracker add 250 food -n "lunch with team"
```

## Usage

```bash
# record expenses
expense add 250 food -n "lunch with team"
expense add 1200 travel -n "cab to airport" -d 2026-06-10

# see where the money went
expense list
expense list -m 2026-06 -c food

# monthly breakdown by category
expense summary -m 2026-06

# remove a wrong entry
expense delete 12

# export for Excel / Google Sheets
expense export june.csv -m 2026-06
```

Example `summary` output:

```
rent            15000.00  (62.5%)
food             5400.00  (22.5%)
travel           3600.00  (15.0%)
------------------------------------
total           24000.00
```

## Data storage

Expenses are stored in `~/.expenses.db` by default. Override with the `--db` flag
or the `EXPENSE_DB` environment variable.

## Running tests

```bash
pip install pytest
pytest
```

## License

MIT — see [LICENSE](LICENSE).
