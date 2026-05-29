from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Customer:
    customer_id: str
    signup_date: date
    country: str


@dataclass(frozen=True)
class Subscription:
    customer_id: str
    start_date: date
    end_date: date | None
    plan: str
    monthly_price: Decimal


@dataclass(frozen=True)
class DataIssue:
    severity: str
    message: str
    row_number: int | None = None
