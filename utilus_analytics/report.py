from __future__ import annotations

from utilus_analytics.loader import find_data_issues
from utilus_analytics.metrics import (
    calculate_monthly_churned_customers,
    calculate_monthly_mrr,
    calculate_signup_cohort_retention,
)
from utilus_analytics.models import Customer, Subscription


def build_report(customers: list[Customer], subscriptions: list[Subscription]) -> dict[str, object]:
    issues = find_data_issues(customers, subscriptions)
    return {
        "monthly_mrr": calculate_monthly_mrr(subscriptions),
        "monthly_churned_customers": calculate_monthly_churned_customers(subscriptions),
        "signup_cohorts_3m_retention": calculate_signup_cohort_retention(customers, subscriptions),
        "data_quality_issues": [
            {
                "severity": issue.severity,
                "message": issue.message,
                "row_number": issue.row_number,
            }
            for issue in issues
        ],
    }
