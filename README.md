# Factory Intelligence

Factory Intelligence is an analytics platform for manufacturing environments.
It is designed to help quality teams and production managers turn CSV exports from lab equipment
and production systems into useful operational insights such as statistical quality analysis,
OEE tracking, and shift-level reporting.

The project is currently in an early-stage scaffold phase, but the long-term goal is to provide
an API-driven workflow for ingestion, validation, analysis, and report generation.

---

## Problem

Manufacturing teams often rely on spreadsheets, paper forms, and manual reporting to monitor quality and production performance. That slows down decision-making and makes it harder to spot trends across shifts, lines, and batches. 
As a former industrial engineer and quality manager, this was a problem I faced every day and never had the right tools to solve.
Factory Intelligence aims to replace part of that workflow with a structured API that can ingest manufacturing data, analyse it, and produce reports with less manual effort.

---

## Current status

This repository currently contains the initial FastAPI project structure, local Docker infrastructure,
and the first SQLAlchemy domain models. The foundation is in place, but several core product features
are still planned or partially implemented.

### Implemented or scaffolded
- FastAPI project structure under the app package
- Containerized local development setup with Docker Compose
- PostgreSQL and LocalStack services for local development
- Environment configuration examples
- Basic API router structure with lab and production health checks
- Initial SQLAlchemy models for production sheets, lab tests, production lines, shifts, resin types, and panel types

### Not yet fully implemented
- Alembic migrations for database schema management
- Pydantic request and response schemas
- CRUD endpoints for lab and production data
- CSV ingestion and parsing workflows
- Lab quality analysis endpoints
- Production OEE and stoppage analysis endpoints
- Async report generation and PDF delivery
- Full test coverage for business logic

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

## Current learning path

The next logical development steps after defining the models are:

1. Add Alembic and create the first database migration
2. Define Pydantic schemas for input and output validation
3. Build simple CRUD endpoints for production sheets and lab tests
4. Add tests for models, database relationships, and basic API behavior
5. Define expected CSV formats and validation rules
6. Build CSV ingestion workflows
7. Add analytics services for quality and production metrics
8. Add report generation and asynchronous delivery workflows

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
├── scripts/
├── tests/
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
git clone https://github.com/[username]/factory-intelligence.git
cd factory-intelligence
cp .env.example .env
docker compose up --build
```

Expected local services:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- LocalStack: http://localhost:4566

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
