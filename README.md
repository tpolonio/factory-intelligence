# Factory Intelligence

Factory Intelligence is an analytics platform for manufacturing environments.
It is designed to help quality teams and production managers turn CSV exports from lab equipment
and production systems into useful operational insights such as statistical quality analysis,
OEE tracking, and shift-level reporting.

The project is in active development. Production sheet workflows are implemented end to end —
creation, filtered querying, detail lookup, and per-run operational assessment — while lab test
endpoints, CSV ingestion, and reporting remain on the roadmap.

---

## Problem

Manufacturing teams often rely on spreadsheets, paper forms, and manual reporting to monitor quality and production performance. That slows down decision-making and makes it harder to spot trends across shifts, lines, and batches. 
As a former industrial engineer and quality manager, this was a problem I faced every day and never had the right tools to solve.
Factory Intelligence aims to replace part of that workflow with a structured API that can ingest manufacturing data, analyse it, and produce reports with less manual effort.

---

## Current Capabilities

Factory Intelligence currently supports reference-data management for production lines, resin
types, and shifts, plus complete production sheet workflows.

Implemented:

- FastAPI application structure with versioned API routing
- Docker Compose local development setup with PostgreSQL and LocalStack
- SQLAlchemy models for production sheets, lab tests, production lines, shifts, resin types, and panel types
- Alembic database migration setup with an initial schema migration
- Pydantic request and response schemas for implemented workflows
- Reference-data endpoints for production lines, resin types, and shifts
- Production sheet creation with reference-record validation
- Production sheet listing with operational filters, pagination, and deterministic ordering (newest first)
- Production sheet detail retrieval
- Per-run operational assessment: quality, downtime, and sustainability statuses with flags and main-issue prioritization
- Process parameter assessment: press temperature, pressure, factor, and forming line speed classified against target windows
- Material efficiency metrics: chemical consumption per accepted panel
- Service-layer business logic for implemented production workflows
- Pytest coverage for reference-data services and production sheet workflows

Not yet implemented:

- Production sheet update and delete workflows
- Lab test schemas and endpoints
- CSV ingestion and parsing workflows
- Lab quality analysis endpoints
- Production OEE and stoppage analysis endpoints
- Product-specific process target configuration (assessment thresholds are currently service-level defaults)
- Async report generation and PDF delivery
- Deployment infrastructure beyond local development

---

## Roadmap

### Phase 1 — foundation
- Finalize the core app entry points and router structure
- Define the initial data models and schemas
- Connect the API to local PostgreSQL and LocalStack services
- Add Alembic migrations for the database schema

### Phase 2 — ingestion and validation
- Build basic CRUD endpoints for lab and production records
- Build CSV upload handlers for lab and production datasets
- Add validation rules for required columns and expected formats
- Introduce domain detection based on CSV headers

### Phase 3 — analytics engine
- Implement quality analysis for lab data
- Implement OEE, Pareto, and shift comparison logic for production data
- Add statistical calculations such as mean, standard deviation, Cpk, and outlier detection

### Phase 4 — reporting and async workflows
- Add background processing for report generation
- Generate PDF reports for lab and production use cases
- Integrate S3 and queue-based workflows for asynchronous delivery

### Phase 5 — deployment readiness
- Expand infrastructure definitions for AWS deployment
- Add more automated tests and CI coverage
- Document sample requests and expected responses

---

## Architecture overview

The proposed architecture is intended to follow a simple pipeline:

1. CSV files are uploaded through the API
2. The data is parsed and validated
3. Business logic computes analytics and stores results
4. Reports are generated asynchronously and delivered via storage/queue-based workflows

The local environment uses Docker Compose with PostgreSQL and LocalStack, while the long-term AWS design
is intended to use services such as S3, SQS, RDS, ECS, Lambda, EventBridge and Terraform.

---

## Domain model overview

The current model layer is centered around two operational records:

- Production sheets capture manufacturing parameters such as line, shift, batch, panel dimensions,
  resin usage, downtime, panels produced, panels rejected, and calculated rejection rate.
- Lab tests capture quality measurements for produced panels, including density, moisture, internal bond,
  bending strength, elastic modulus, swelling, water absorption, and formaldehyde metrics.

Shared reference models currently include:

- Production lines
- Shifts
- Resin types
- Panel types

Production and lab records are connected through shared concepts such as production line, shift, batch,
panel type, and panel thickness. A future `Batch` model may become useful if batch-level traceability
needs to become a first-class part of the application.

---

## Project structure

```
factory-intelligence/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── reports/
│   ├── schemas/
│   └── services/
├── alembic/
├── docs/
├── scripts/
├── tests/
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Local setup

Requirements:
- Docker Desktop with the WSL2 backend on Windows
- Docker Compose v2

```bash
git clone https://github.com/TPolonio/factory-intelligence.git
cd factory-intelligence
cp .env.example .env
docker compose up --build
```

Expected local services:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- LocalStack: http://localhost:4566

Run tests:

```bash
.venv/bin/python -m pytest -q
```

API tests use `httpx2.AsyncClient` with an in-process ASGI transport instead of
FastAPI's sync `TestClient`. This keeps the tests compatible with the current
FastAPI/Starlette/Python stack while still exercising the real HTTP routes.

---

## Tech stack

- API: FastAPI, Python
- Database: PostgreSQL, SQLAlchemy
- Validation: Pydantic, pydantic-settings
- Infrastructure: Docker Compose, AWS-oriented local development with LocalStack
- Reporting: ReportLab
- Local emulation: LocalStack

---

## License

MIT
