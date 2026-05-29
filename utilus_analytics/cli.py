from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utilus_analytics.loader import InputValidationError, load_customers, load_subscriptions
from utilus_analytics.report import build_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a JSON subscription analytics report from customer and subscription CSV exports.",
        epilog=(
            "Example: python main.py customers.csv subscriptions.csv output.json\n\n"
            "The report includes monthly MRR, monthly churned customers, "
            "3-month signup cohort retention, and non-fatal data quality warnings."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("customers_csv", type=Path, help="Path to customers.csv")
    parser.add_argument("subscriptions_csv", type=Path, help="Path to subscriptions.csv")
    parser.add_argument("output_json", type=Path, help="Path where the JSON report will be written")
    args = parser.parse_args(argv)

    errors: list[str] = []
    try:
        customers = load_customers(args.customers_csv)
    except InputValidationError as exc:
        customers = []
        errors.extend(exc.messages)
    try:
        subscriptions = load_subscriptions(args.subscriptions_csv)
    except InputValidationError as exc:
        subscriptions = []
        errors.extend(exc.messages)

    if errors:
        print("Input error:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    report = build_report(customers, subscriptions)

    for issue in report["data_quality_issues"]:
        print(f"{issue['severity'].upper()}: {issue['message']}", file=sys.stderr)

    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0
