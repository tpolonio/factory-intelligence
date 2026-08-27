import pytest

from tests.helpers import build_production_sheet_payload

pytestmark = pytest.mark.anyio


async def create_production_line(client):
    create_line_response = await client.post(
        url="/api/v1/production/lines",
        json={
            "name": "Line 1",
        },
    )
    assert create_line_response.status_code == 201, create_line_response.json()

    return create_line_response.json()


async def create_shift(client):
    create_shift_response = await client.post(
        url="/api/v1/production/shifts",
        json={
            "shift_letter": "A",
            "press_operator": "Joao Fernandes",
            "line_operator": "Luis Costa",
        },
    )
    assert create_shift_response.status_code == 201, create_shift_response.json()
    return create_shift_response.json()


async def create_resin_type(client):
    create_resin_response = await client.post(
        url="/api/v1/production/resin-types",
        json={
            "name": "UF",
        },
    )
    assert create_resin_response.status_code == 201, create_resin_response.json()
    return create_resin_response.json()


async def test_create_production_sheet_through_api(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    payload = build_production_sheet_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        resin_type_id=resin_type_id,
    ).model_dump(mode="json")

    response = await client.post(
        url="/api/v1/production/production-sheets",
        json=payload,
    )

    body = response.json()

    assert response.status_code == 201, response.json()
    assert body["production_line_id"] == line_id
    assert body["shift_id"] == shift_id
    assert body["resin_type_id"] == resin_type_id


async def test_get_production_sheet_through_api(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    payload = build_production_sheet_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        resin_type_id=resin_type_id,
    ).model_dump(mode="json")

    new_production_sheet = await client.post(
        url="/api/v1/production/production-sheets",
        json=payload,
    )

    created_sheet_id = new_production_sheet.json()["id"]

    response = await client.get(
        url=f"/api/v1/production/production-sheets/{created_sheet_id}",
    )

    body = response.json()

    assert response.status_code == 200, response.json()
    assert body["id"] == created_sheet_id
    assert body["production_line_id"] == line_id
    assert body["shift_id"] == shift_id
    assert body["resin_type_id"] == resin_type_id


async def test_get_production_sheet_assessment_through_api_returns_ok(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    payload = build_production_sheet_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        resin_type_id=resin_type_id,
    ).model_dump(mode="json")

    new_production_sheet = await client.post(
        url="/api/v1/production/production-sheets",
        json=payload,
    )

    assert new_production_sheet.status_code == 201, new_production_sheet.json()

    created_sheet_id = new_production_sheet.json()["id"]

    response = await client.get(
        url=f"/api/v1/production/production-sheets/{created_sheet_id}/assessment",
    )

    body = response.json()

    assert response.status_code == 200, response.json()
    assert body["production_metrics"]["accepted_panels"] == 95
    assert body["quality"]["status"] == "warning"
    assert body["process_parameters"]["press_temperature"]["status"] == "within_target"
    assert body["material_efficiency"]["resin_per_accepted_panel"] == "0.11"
    assert body["flags"] == [
        "high_rejection_rate",
        "downtime_above_target",
        "recycled_material_below_target",
    ]
    assert body["main_issue"] == "high_rejection_rate"


async def test_get_production_sheet_assessment_through_api_returns_not_found(client):

    response = await client.get(
        url="/api/v1/production/production-sheets/99/assessment",
    )

    assert response.status_code == 404, response.json()
