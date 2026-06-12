"""Command line interface for the expense tracker."""

import argparse
import sys
from datetime import datetime

from .db import ExpenseDB


def valid_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date (expected YYYY-MM-DD)")


def valid_month(value):
    try:
        datetime.strptime(value, "%Y-%m")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid month (expected YYYY-MM)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="expense",
        description="Track your daily expenses from the terminal.",
    )
    parser.add_argument("--db", help="path to the SQLite database file", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record a new expense")
    add.add_argument("amount", type=float, help="amount spent")
    add.add_argument("category", help="category, e.g. food, travel, rent")
    add.add_argument("-n", "--note", default="", help="optional note")
    add.add_argument("-d", "--date", type=valid_date, default=None, help="date as YYYY-MM-DD (default: today)")

    lst = sub.add_parser("list", help="list expenses")
    lst.add_argument("-m", "--month", type=valid_month, default=None, help="filter by month (YYYY-MM)")
    lst.add_argument("-c", "--category", default=None, help="filter by category")

    summary = sub.add_parser("summary", help="show total spend per category")
    summary.add_argument("-m", "--month", type=valid_month, default=None, help="filter by month (YYYY-MM)")

    delete = sub.add_parser("delete", help="delete an expense by id")
    delete.add_argument("id", type=int, help="expense id (see 'list')")

    export = sub.add_parser("export", help="export expenses to a CSV file")
    export.add_argument("file", help="output CSV path")
    export.add_argument("-m", "--month", type=valid_month, default=None, help="filter by month (YYYY-MM)")

    return parser


def print_table(rows):
    if not rows:
        print("No expenses found.")
        return
    print(f"{'ID':>4}  {'Date':<10}  {'Amount':>10}  {'Category':<12}  Note")
    print("-" * 60)
    total = 0.0
    for row in rows:
        total += row["amount"]
        print(f"{row['id']:>4}  {row['spent_on']:<10}  {row['amount']:>10.2f}  {row['category']:<12}  {row['note']}")
    print("-" * 60)
    print(f"{'Total':>28}: {total:.2f}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    db = ExpenseDB(args.db)
    try:
        if args.command == "add":
            expense_id = db.add(args.amount, args.category, args.note, args.date)
            print(f"Added expense #{expense_id}: {args.amount:.2f} on {args.category}")
        elif args.command == "list":
            print_table(db.list(month=args.month, category=args.category))
        elif args.command == "summary":
            rows = db.summary(month=args.month)
            if not rows:
                print("No expenses found.")
            else:
                grand_total = sum(row["total"] for row in rows)
                for row in rows:
                    pct = (row["total"] / grand_total) * 100
                    print(f"{row['category']:<12}  {row['total']:>10.2f}  ({pct:.1f}%)")
                print("-" * 36)
                print(f"{'total':<12}  {grand_total:>10.2f}")
        elif args.command == "delete":
            if db.delete(args.id):
                print(f"Deleted expense #{args.id}")
            else:
                print(f"No expense with id {args.id}", file=sys.stderr)
                return 1
        elif args.command == "export":
            count = db.export_csv(args.file, month=args.month)
            print(f"Exported {count} expenses to {args.file}")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
