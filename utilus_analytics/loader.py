from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from utilus_analytics.models import Customer, DataIssue, Subscription


class InputValidationError(ValueError):
    """Raised when an input CSV cannot be parsed into the required schema."""


CUSTOMER_COLUMNS = {"customer_id", "signup_date", "country"}
SUBSCRIPTION_COLUMNS = {
    "customer_id",
    "start_date",
    "end_date",
    "plan",
    "monthly_price",
}


def load_customers(path: Path) -> list[Customer]:
    rows = _read_csv(path, CUSTOMER_COLUMNS)
    customers: list[Customer] = []
    seen: set[str] = set()

    for row_number, row in rows:
        customer_id = row["customer_id"].strip()
        if not customer_id:
            raise InputValidationError(f"{path}: row {row_number} has empty customer_id")
        if customer_id in seen:
            raise InputValidationError(f"{path}: duplicate customer_id {customer_id!r} on row {row_number}")
        seen.add(customer_id)
        customers.append(
            Customer(
                customer_id=customer_id,
                signup_date=_parse_date(row["signup_date"], path, row_number, "signup_date"),
                country=row["country"].strip(),
            )
        )
    return customers


def load_subscriptions(path: Path) -> list[Subscription]:
    rows = _read_csv(path, SUBSCRIPTION_COLUMNS)
    subscriptions: list[Subscription] = []

    for row_number, row in rows:
        customer_id = row["customer_id"].strip()
        if not customer_id:
            raise InputValidationError(f"{path}: row {row_number} has empty customer_id")
        start_date = _parse_date(row["start_date"], path, row_number, "start_date")
        end_date = _parse_optional_date(row["end_date"], path, row_number, "end_date")
        if end_date is not None and end_date < start_date:
            raise InputValidationError(f"{path}: row {row_number} end_date is before start_date")

        subscriptions.append(
            Subscription(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                plan=row["plan"].strip(),
                monthly_price=_parse_decimal(row["monthly_price"], path, row_number),
            )
        )
    return subscriptions


def find_data_issues(customers: list[Customer], subscriptions: list[Subscription]) -> list[DataIssue]:
    customer_ids = {customer.customer_id for customer in customers}
    issues: list[DataIssue] = []
    for index, subscription in enumerate(subscriptions, start=2):
        if subscription.customer_id not in customer_ids:
            issues.append(
                DataIssue(
                    severity="warning",
                    message=f"subscription references unknown customer_id {subscription.customer_id!r}",
                    row_number=index,
                )
            )
    return issues


def _read_csv(path: Path, required_columns: set[str]) -> list[tuple[int, dict[str, str]]]:
    if not path.exists():
        raise InputValidationError(f"{path}: file does not exist")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(required_columns - fieldnames)
        if missing:
            raise InputValidationError(f"{path}: missing required columns: {', '.join(missing)}")
        return [(row_number, row) for row_number, row in enumerate(reader, start=2)]


def _parse_date(raw_value: str, path: Path, row_number: int, column: str) -> date:
    try:
        return date.fromisoformat(raw_value.strip())
    except ValueError as exc:
        raise InputValidationError(f"{path}: row {row_number} has malformed {column}: {raw_value!r}") from exc


def _parse_optional_date(raw_value: str, path: Path, row_number: int, column: str) -> date | None:
    if not raw_value.strip():
        return None
    return _parse_date(raw_value, path, row_number, column)


def _parse_decimal(raw_value: str, path: Path, row_number: int) -> Decimal:
    try:
        value = Decimal(raw_value.strip())
    except InvalidOperation as exc:
        raise InputValidationError(f"{path}: row {row_number} has malformed monthly_price: {raw_value!r}") from exc
    if value < 0:
        raise InputValidationError(f"{path}: row {row_number} monthly_price cannot be negative")
    return value
