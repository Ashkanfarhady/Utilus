# Assumptions

## Reporting Range

Open-ended active subscriptions do not imply an infinite report. By default, monthly MRR is reported from the first subscription start month through the latest known date in the subscription export.

## Active Subscription Boundaries

Subscription date boundaries are inclusive. A subscription is considered active on its `start_date` and on its `end_date`.

## Monthly MRR

A subscription contributes its full `monthly_price` to a calendar month if it is active on any day in that month. The implementation does not prorate partial months.

## Churn

A subscription with an `end_date` is treated as churn only if the same customer does not start a later subscription within 30 days after that end date. A subscription starting exactly 30 days later is considered within the grace window and prevents churn.

## Cohort Retention

Three-month retention is checked on the exact date three calendar months after signup. For end-of-month dates, the target date is clamped to the last valid day of the target month.

## Data Quality

Malformed required fields are fatal input errors. Non-fatal issues, such as a subscription referencing an unknown customer, are included in `data_quality_issues` and printed as warnings.

The provided CSV files currently contain malformed fields, so the CLI correctly fails validation until those inputs are corrected.
