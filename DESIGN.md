# Design

## Structure

The CLI entry point is intentionally small:

- `main.py` delegates to `utilus_analytics.cli`.
- `loader.py` validates and parses CSV input into typed dataclasses.
- `metrics.py` contains the business calculations.
- `report.py` composes the final JSON-ready report.
- `tests/` covers metric behavior, validation, and the CLI path.

This keeps `main.py` from becoming a large script and makes each metric testable without file I/O.

## Business Rules

Monthly MRR is calculated by calendar month. A subscription contributes its full `monthly_price` to a month if it is active on any day in that month. Date boundaries are inclusive, so a subscription ending on the first day of a month still counts for that month.

Churn is counted in the month of a subscription `end_date`. A churn event occurs only when the same customer has no later subscription starting more than the end date and within 30 days after that end date. A re-subscription exactly 30 days later prevents churn.

Signup cohorts are grouped by `signup_date` month. For each customer, the 3-month retention check uses the exact calendar date three months after signup, clamped for shorter months by Python calendar logic in `dates.add_months`. A customer is retained if any subscription is active on that date.

## Extending Metrics

New metrics can be added as standalone functions in `metrics.py` and then included in `report.build_report`. For larger growth, each metric could move into its own module with a shared interface, while the loader and CLI remain unchanged.

## Assumptions and Trade-offs

Open-ended active subscriptions cannot produce infinite future MRR. The default report range runs from the first subscription start month through the latest known date in the subscription export.

Malformed required fields are treated as fatal input errors with clear messages. Data quality issues that do not prevent parsing, such as subscriptions referencing unknown customers, are surfaced as warnings and included in the JSON report.
