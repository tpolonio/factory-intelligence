# Factory Intelligence

An analytics API for industrial manufacturing environments.
Ingests CSV exports from production lines and lab equipment,
runs statistical quality analysis and OEE calculations,
and generates shift reports asynchronously.

Built with FastAPI, PostgreSQL, and AWS — designed for wood panel manufacturing
but applicable to any discrete or continuous production environment.

---

## Problem

Quality managers in manufacturing plants typically rely on spreadsheets and paper forms
to track production KPIs, quality test results, and non-conformities.
This creates delays in detecting trends, makes shift reporting a manual burden,
and leaves root cause data buried in files no one reads.

This project replaces that workflow with two focused APIs:
one for lab quality tests, one for production line indicators.

---

## Two domains

### Lab — quality test analysis (`/lab/`)

Accepts CSV exports from lab equipment with test results per panel batch.
Validates each parameter against EN 312 / EN 622 limits,
calculates statistical indicators including Cpk, mean, standard deviation, and outliers (1.5 × IQR),
and flags non-conformities with suggested actions.

**Cpk** (process capability index) measures how well a production process stays within
specification limits — a value above 1.33 is generally considered capable.
Calculating it per parameter and per line over time is the core quality signal this API provides.

**CSV input columns:**
`line_id, shift_id, panel_ref, thickness_mm, density_kg_m3, moisture_pct, internal_bond_n_mm2, tested_at`

**Key endpoints:**
- `POST /api/v1/lab/upload` — ingest and validate a test results CSV; queues processing via SQS
- `GET /api/v1/lab/summary?line=&from=&to=` — aggregated stats by line and period
- `GET /api/v1/lab/trends/{parameter}` — time series for a given test parameter
- `GET /api/v1/lab/cpk?line=&parameter=&from=&to=` — Cpk trend over a period
- `POST /api/v1/lab/report/{shift_id}` — generate PDF non-conformity report (async, stored in S3)

### Production — OEE and line indicators (`/production/`)

Accepts CSV exports from production systems with shift-level KPIs.
Calculates OEE (availability × performance × quality),
produces Pareto analysis of stoppages by category,
and generates end-of-shift PDF reports asynchronously.

**CSV input columns:**
`line_id, shift_id, panels_produced, panels_rejected, planned_downtime_min, unplanned_downtime_min, stoppage_category, recorded_at`

**Key endpoints:**
- `POST /api/v1/production/upload` — ingest a production shift CSV; queues processing via SQS
- `GET /api/v1/production/oee?line=&from=&to=` — OEE breakdown by period
- `GET /api/v1/production/stoppages/pareto` — stoppage Pareto analysis by category
- `GET /api/v1/production/compare?shift_a=&shift_b=` — side-by-side shift comparison
- `POST /api/v1/production/report/{shift_id}` — generate PDF shift report (async, stored in S3)

### Async report generation

PDF reports are generated asynchronously via SQS.
When a report is requested, a message is queued and a worker processes it in the background.
Once the PDF is stored in S3, an optional webhook callback notifies the requester.
In local development, LocalStack emulates both SQS and S3.

---

## Architecture

```
CSV upload (POST)
      │
      ▼
CSV parser service     ← detects domain from headers
      │
      ├── lab domain
      └── production domain
              │
              ▼
         FastAPI routers  (/api/v1/lab · /api/v1/production)
              │
      ┌───────┴────────────┐
      ▼                    ▼
 PostgreSQL            SQS queue
                           │
                           ▼
                     report worker
                           │
                           ▼
                      S3 (PDF) ──► webhook callback (optional)
```

**Local development** uses Docker Compose with LocalStack for SQS and S3 emulation.

**Production design** (documented, not deployed) uses:
S3 (CSV drop zone) → EventBridge rule → Lambda (parser) → ECS Fargate (FastAPI) → RDS PostgreSQL + SQS

The business logic is identical in both environments — only the trigger changes.
See [`/infra`](./infra) for the full Terraform definition.

---

## Project structure

```
factory-intelligence/
├── app/
│   ├── main.py                     # FastAPI entry point
│   ├── core/
│   │   ├── config.py               # environment variables (pydantic-settings)
│   │   └── database.py             # SQLAlchemy engine and session
│   ├── api/v1/
│   │   ├── router.py               # aggregates all routers
│   │   ├── lab.py                  # /lab/ endpoints
│   │   └── production.py           # /production/ endpoints
│   ├── models/
│   │   ├── lab.py                  # lab database models (SQLAlchemy)
│   │   └── production.py           # production database models
│   ├── schemas/
│   │   ├── lab.py                  # lab request/response schemas (Pydantic)
│   │   └── production.py           # production request/response schemas
│   ├── services/
│   │   ├── csv_parser.py           # reads CSV, detects domain
│   │   ├── lab_analysis.py         # Cpk, trends, non-conformity logic
│   │   └── production_analysis.py  # OEE, Pareto, shift comparison logic
│   └── reports/
│       ├── pdf_lab.py              # generates non-conformity PDF
│       └── pdf_production.py       # generates shift report PDF
├── infra/
│   ├── modules/
│   │   ├── networking/             # VPC, subnets, security groups
│   │   ├── database/               # RDS PostgreSQL
│   │   ├── compute/                # ECS Fargate + ALB
│   │   └── storage/                # S3 + IAM
│   └── environments/
│       ├── dev/
│       └── prod/
├── scripts/
│   └── init-aws.sh                 # creates S3 bucket and SQS queue in LocalStack
├── tests/
│   ├── test_lab.py
│   └── test_production.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Running costs

**This project runs at zero cost locally.**
All AWS services are emulated via LocalStack inside Docker Compose —
no AWS account required to run, develop, or test the full feature set.

| Environment | Cost | How |
|---|---|---|
| Local development | €0 | Docker Compose + LocalStack (S3, SQS emulation) |
| AWS deployment | ~€10–15/month | ECS Fargate + RDS t3.micro + S3 + SQS |

The Terraform code in `/infra` is written and ready but intentionally not applied.
To deploy to AWS: `cd infra/environments/dev && terraform init && terraform apply`.
To tear it down and stop all costs: `terraform destroy`.

This design decision is deliberate — a portfolio project should not incur ongoing costs
when it is not actively being demonstrated.

---

## Local setup

**Requirements:** Docker Desktop with WSL2 backend, Docker Compose v2

```bash
git clone https://github.com/[username]/factory-intelligence.git
cd factory-intelligence
cp .env.example .env
docker compose up --build
```

| Endpoint | URL |
|---|---|
| API health | http://localhost:8000/health |
| Interactive docs (Swagger) | http://localhost:8000/docs |
| Alternative docs (ReDoc) | http://localhost:8000/redoc |
| LocalStack (AWS emulation) | http://localhost:4566 |

---

## Why this exists

I spent 6 years working in quality and production in a wood panel manufacturing plant
before moving into software engineering.

This is the tool I wished existed when I was filling in shift reports by hand at 6am
and trying to spot a density trend, or a humidity spike across different productions.

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI · Python 3.12 |
| Database | PostgreSQL 15 · SQLAlchemy · Alembic |
| Validation | Pydantic v2 · pydantic-settings |
| Queue | SQS (AWS) · LocalStack (local dev) |
| Reports | ReportLab (PDF) · openpyxl (Excel) |
| Infrastructure | Terraform · AWS (ECS, RDS, S3, SQS, Lambda, EventBridge) |
| Local dev | Docker Compose · LocalStack |
| CI/CD | GitHub Actions |

---

## License

MIT
>>>>>>> 06a61b0 (feat(fi): initial project structure)
