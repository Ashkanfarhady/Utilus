from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utilus_analytics.loader import InputValidationError, load_customers, load_subscriptions
from utilus_analytics.report import build_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate subscription analytics from CSV exports.")
    parser.add_argument("customers_csv", type=Path)
    parser.add_argument("subscriptions_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args(argv)

    try:
        customers = load_customers(args.customers_csv)
        subscriptions = load_subscriptions(args.subscriptions_csv)
        report = build_report(customers, subscriptions)
    except InputValidationError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1

    for issue in report["data_quality_issues"]:
        print(f"{issue['severity'].upper()}: {issue['message']}", file=sys.stderr)

    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0
