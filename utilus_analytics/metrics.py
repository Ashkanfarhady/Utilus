from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from utilus_analytics.dates import add_months, iter_month_starts, month_end, month_key
from utilus_analytics.models import Customer, Subscription


def calculate_monthly_mrr(subscriptions: list[Subscription], report_end: date | None = None) -> dict[str, str]:
    if not subscriptions:
        return {}

    start = min(subscription.start_date for subscription in subscriptions)
    end = report_end or _default_report_end(subscriptions, start)
    monthly_mrr: dict[str, str] = {}

    for month in iter_month_starts(start, end):
        active_total = sum(
            subscription.monthly_price
            for subscription in subscriptions
            if subscription_is_active_during_month(subscription, month)
        )
        monthly_mrr[month_key(month)] = _money(active_total)

    return monthly_mrr


def calculate_monthly_churned_customers(subscriptions: list[Subscription]) -> dict[str, int]:
    subscriptions_by_customer = _subscriptions_by_customer(subscriptions)
    churned_by_month: dict[str, set[str]] = defaultdict(set)

    for subscription in subscriptions:
        if subscription.end_date is None:
            continue
        later_subscriptions = [
            candidate
            for candidate in subscriptions_by_customer[subscription.customer_id]
            if subscription.end_date < candidate.start_date <= subscription.end_date + timedelta(days=30)
        ]
        if not later_subscriptions:
            churned_by_month[month_key(subscription.end_date)].add(subscription.customer_id)

    return {month: len(customer_ids) for month, customer_ids in sorted(churned_by_month.items())}


def calculate_signup_cohort_retention(
    customers: list[Customer], subscriptions: list[Subscription]
) -> dict[str, dict[str, int | float]]:
    subscriptions_by_customer = _subscriptions_by_customer(subscriptions)
    customers_by_cohort: dict[str, list[Customer]] = defaultdict(list)
    for customer in customers:
        customers_by_cohort[month_key(customer.signup_date)].append(customer)

    cohorts: dict[str, dict[str, int | float]] = {}
    for cohort_month, cohort_customers in sorted(customers_by_cohort.items()):
        active_after_3_months = 0
        for customer in cohort_customers:
            target_date = add_months(customer.signup_date, 3)
            if any(
                subscription_is_active_on(subscription, target_date)
                for subscription in subscriptions_by_customer.get(customer.customer_id, [])
            ):
                active_after_3_months += 1

        cohort_size = len(cohort_customers)
        cohorts[cohort_month] = {
            "cohort_size": cohort_size,
            "active_after_3_months": active_after_3_months,
            "retention_rate_3m": round(active_after_3_months / cohort_size, 4) if cohort_size else 0.0,
        }
    return cohorts


def subscription_is_active_on(subscription: Subscription, target_date: date) -> bool:
    return subscription.start_date <= target_date and (
        subscription.end_date is None or subscription.end_date >= target_date
    )


def subscription_is_active_during_month(subscription: Subscription, month_start: date) -> bool:
    return subscription.start_date <= month_end(month_start) and (
        subscription.end_date is None or subscription.end_date >= month_start
    )


def _subscriptions_by_customer(subscriptions: list[Subscription]) -> dict[str, list[Subscription]]:
    grouped: dict[str, list[Subscription]] = defaultdict(list)
    for subscription in subscriptions:
        grouped[subscription.customer_id].append(subscription)
    for customer_subscriptions in grouped.values():
        customer_subscriptions.sort(key=lambda subscription: subscription.start_date)
    return grouped


def _default_report_end(subscriptions: list[Subscription], fallback: date) -> date:
    known_end_dates = [subscription.end_date for subscription in subscriptions if subscription.end_date is not None]
    known_dates = [subscription.start_date for subscription in subscriptions] + known_end_dates
    return max(known_dates, default=fallback)


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01")))
