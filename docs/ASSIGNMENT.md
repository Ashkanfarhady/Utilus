# Assignment Summary

Build a small Python CLI for a subscription SaaS analytics export.

## Inputs

`customers.csv`

- `customer_id`
- `signup_date`
- `country`

`subscriptions.csv`

- `customer_id`
- `start_date`
- `end_date`
- `plan`
- `monthly_price`

## Output

The CLI writes a JSON report containing:

- Monthly MRR by calendar month.
- Monthly churned customer counts.
- Signup cohorts with 3-month retention.
- Data quality issues surfaced during loading or validation.

## CLI

```bash
python main.py customers.csv subscriptions.csv output.json
```

## Required Supporting Work

- Clear input validation and error messages.
- Data quality warnings, including subscription rows for unknown customers.
- Tests for churn logic, retention logic, and edge cases.
- Short design note.
- AI usage note with relevant prompts or summaries.
