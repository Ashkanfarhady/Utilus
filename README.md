# Utilus Home Assessment

Python CLI for generating subscription SaaS analytics from customer and subscription CSV exports.

## Usage

```bash
python3 main.py customers.csv subscriptions.csv output.json
```

The command writes a JSON report with:

- `monthly_mrr`
- `monthly_churned_customers`
- `signup_cohorts_3m_retention`
- `data_quality_issues`

If required columns are missing or fields are malformed, the command exits with a non-zero status and prints a clear input error.

CLI help is available with:

```bash
python3 main.py --help
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The runtime implementation uses only the Python standard library. `pytest` and `pytest-cov` are listed for tests and coverage.

## Make Commands

```bash
make help
make install
make test
make coverage
make run
make docker-build
make docker-run
```

## Tests

```bash
python3 -m pytest -q
```

Coverage:

```bash
python3 -m pytest --cov=utilus_analytics --cov-report=term-missing
```

## Docker

Build the image:

```bash
docker build -t utilus-analytics .
```

Run the CLI in Docker:

```bash
docker run --rm -v "$(pwd):/app" utilus-analytics customers.csv subscriptions.csv output.json
```

## Notes on Provided CSVs

The provided CSV files currently include malformed fields that correctly trigger validation failures:

- `customers.csv` row 20 has invalid `signup_date` value `2024-13-05`.
- `customers.csv` row 40 contains duplicate `customer_id` value `C038`.
- `subscriptions.csv` row 9 has invalid `end_date` value `2024-02-30`.
- `subscriptions.csv` row 31 has invalid `monthly_price` value `thirty`.
- `subscriptions.csv` row 37 has `end_date` before `start_date`.

I did not alter the input files; the validation behavior is part of the solution.

## Repository Structure

```text
.
├── DESIGN.md
├── docs/
│   ├── ASSIGNMENT.md
│   ├── AI_USAGE.md
│   └── ASSUMPTIONS.md
├── tests/
├── utilus_analytics/
├── Dockerfile
├── Makefile
├── main.py
├── requirements.txt
└── README.md
```

## Development Approach

I am keeping the work in small, focused commits so the implementation history shows the progression from setup, to solution design, to implementation, tests, and documentation.

See [DESIGN.md](DESIGN.md) for the design note and [docs/AI_USAGE.md](docs/AI_USAGE.md) for the AI assistance note.
