from __future__ import annotations

import json
from pathlib import Path

from utilus_analytics.cli import main
from utilus_analytics.loader import InputValidationError, load_customers, load_subscriptions
from utilus_analytics.report import build_report


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_loader_fails_with_clear_message_for_missing_required_columns(tmp_path: Path) -> None:
    customers_csv = write(
        tmp_path / "customers.csv",
        "customer_id,country\n"
        "c1,NL\n",
    )

    try:
        load_customers(customers_csv)
    except InputValidationError as exc:
        assert "missing required columns: signup_date" in str(exc)
    else:
        raise AssertionError("expected InputValidationError")


def test_report_surfaces_unknown_customer_issue(tmp_path: Path) -> None:
    customers_csv = write(
        tmp_path / "customers.csv",
        "customer_id,signup_date,country\n"
        "c1,2024-01-01,NL\n",
    )
    subscriptions_csv = write(
        tmp_path / "subscriptions.csv",
        "customer_id,start_date,end_date,plan,monthly_price\n"
        "unknown,2024-01-01,,pro,20\n",
    )

    report = build_report(load_customers(customers_csv), load_subscriptions(subscriptions_csv))

    assert report["data_quality_issues"] == [
        {
            "severity": "warning",
            "message": "subscription references unknown customer_id 'unknown'",
            "row_number": 2,
        }
    ]


def test_cli_writes_json_report(tmp_path: Path) -> None:
    customers_csv = write(
        tmp_path / "customers.csv",
        "customer_id,signup_date,country\n"
        "c1,2024-01-01,NL\n",
    )
    subscriptions_csv = write(
        tmp_path / "subscriptions.csv",
        "customer_id,start_date,end_date,plan,monthly_price\n"
        "c1,2024-01-01,,basic,15\n",
    )
    output_json = tmp_path / "report.json"

    assert main([str(customers_csv), str(subscriptions_csv), str(output_json)]) == 0

    report = json.loads(output_json.read_text(encoding="utf-8"))
    assert report["monthly_mrr"] == {"2024-01": "15.00"}
    assert report["signup_cohorts_3m_retention"]["2024-01"]["cohort_size"] == 1
