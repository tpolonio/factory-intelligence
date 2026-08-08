import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.schemas.production import ProductionSheetCreate

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_production_line(client):
    create_line_response = client.post(
        url="/api/v1/production/lines",
        json={
            "name": "Line 1",
        },
    )
    assert create_line_response.status_code == 201, create_line_response.json()

    return create_line_response.json()


def create_shift(client):
    create_shift_response = client.post(
        url="/api/v1/production/shifts",
        json={
            "shift_letter": "A",
            "press_operator": "Joao Fernandes",
            "line_operator": "Luis Costa",
        },
    )
    assert create_shift_response.status_code == 201, create_shift_response.json()
    return create_shift_response.json()


def create_resin_type(client):
    create_resin_response = client.post(
        url="/api/v1/production/resin-types",
        json={
            "name": "UF",
        },
    )
    assert create_resin_response.status_code == 201, create_resin_response.json()
    return create_resin_response.json()


def build_production_sheet_payload(**overrides):
    data = {
        "production_ref": 1,
        "production_line_id": 1,
        "shift_id": 1,
        "resin_type_id": 1,
        "batch_id": 1,
        "production_date": datetime.now(timezone.utc),
        "panel_type": "MDF",
        "panel_length": 4880,
        "panel_width": 1200,
        "panel_thickness": 18,
        "forming_line_speed": 10.5,
        "press_temperature": 180.0,
        "press_pressure": 150.0,
        "press_factor": 0.8,
        "production_duration": 150.5,
        "total_downtime": 20.4,
        "resin_dosed": 12,
        "paraffin_dosed": 4,
        "urea_dosed": 0.5,
        "percentage_recycled_material": 12,
        "panels_produced": 123,
        "panels_rejected": 8,
    }
    data.update(overrides)
    return ProductionSheetCreate(**data)


def test_create_production_sheet_through_api():

    try:
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        create_line_response = create_production_line(client)
        create_shift_response = create_shift(client)
        create_resin_response = create_resin_type(client)

        line_id = create_line_response["id"]
        shift_id = create_shift_response["id"]
        resin_type_id = create_resin_response["id"]

        payload = build_production_sheet_payload(
            production_line_id=line_id, shift_id=shift_id, resin_type_id=resin_type_id
        ).model_dump(mode="json")

        response = client.post(
            url="/api/v1/production/production-sheets",
            json=payload,
        )

        body = response.json()

        assert response.status_code == 201, response.json()
        assert body["production_line_id"] == line_id
        assert body["shift_id"] == shift_id
        assert body["resin_type_id"] == resin_type_id
    finally:
        app.dependency_overrides.clear()


def test_get_production_sheet_through_api():

    try:
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)

        create_line_response = create_production_line(client)
        create_shift_response = create_shift(client)
        create_resin_response = create_resin_type(client)

        line_id = create_line_response["id"]
        shift_id = create_shift_response["id"]
        resin_type_id = create_resin_response["id"]

        payload = build_production_sheet_payload(
            production_line_id=line_id, shift_id=shift_id, resin_type_id=resin_type_id
        ).model_dump(mode="json")

        new_production_sheet = client.post(
            url="/api/v1/production/production-sheets",
            json=payload,
        )

        created_sheet_id = new_production_sheet.json()["id"]

        response = client.get(
            url=f"/api/v1/production/production-sheets/{created_sheet_id}",
        )

        body = response.json()

        assert response.status_code == 200, response.json()
        assert body["id"] == created_sheet_id
        assert body["production_line_id"] == line_id
        assert body["shift_id"] == shift_id
        assert body["resin_type_id"] == resin_type_id
    finally:
        app.dependency_overrides.clear()
