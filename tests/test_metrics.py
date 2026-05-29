from __future__ import annotations

from datetime import date
from decimal import Decimal

from utilus_analytics.metrics import (
    calculate_monthly_churned_customers,
    calculate_monthly_mrr,
    calculate_signup_cohort_retention,
)
from utilus_analytics.models import Customer, Subscription


def subscription(
    customer_id: str,
    start_date: date,
    end_date: date | None,
    monthly_price: str = "10.00",
) -> Subscription:
    return Subscription(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        plan="basic",
        monthly_price=Decimal(monthly_price),
    )


def test_churn_excludes_resubscription_within_30_days_including_boundary() -> None:
    subscriptions = [
        subscription("c1", date(2024, 1, 1), date(2024, 1, 31)),
        subscription("c1", date(2024, 3, 1), None),  # exactly 30 days after Jan 31
        subscription("c2", date(2024, 1, 1), date(2024, 1, 31)),
        subscription("c2", date(2024, 3, 2), None),  # 31 days after Jan 31
    ]

    assert calculate_monthly_churned_customers(subscriptions) == {"2024-01": 1}


def test_retention_uses_exact_three_month_anniversary_and_inclusive_end_date() -> None:
    customers = [
        Customer("c1", date(2024, 1, 15), "NL"),
        Customer("c2", date(2024, 1, 31), "DE"),
        Customer("c3", date(2024, 1, 31), "NL"),
    ]
    subscriptions = [
        subscription("c1", date(2024, 1, 15), date(2024, 4, 15)),
        subscription("c2", date(2024, 1, 31), date(2024, 4, 29)),
        subscription("c3", date(2024, 2, 1), None),
    ]

    assert calculate_signup_cohort_retention(customers, subscriptions) == {
        "2024-01": {
            "cohort_size": 3,
            "active_after_3_months": 2,
            "retention_rate_3m": 0.6667,
        }
    }


def test_monthly_mrr_counts_subscriptions_active_any_day_in_month() -> None:
    subscriptions = [
        subscription("c1", date(2024, 1, 31), date(2024, 2, 1), "25.00"),
        subscription("c2", date(2024, 2, 15), None, "50.00"),
    ]

    assert calculate_monthly_mrr(subscriptions, report_end=date(2024, 3, 1)) == {
        "2024-01": "25.00",
        "2024-02": "75.00",
        "2024-03": "50.00",
    }
