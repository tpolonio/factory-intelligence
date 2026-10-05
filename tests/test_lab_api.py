import pytest

from tests.helpers import build_lab_test_payload, build_production_sheet_payload

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


async def create_production_sheet(client, line_id, shift_id, resin_type_id):
    payload = build_production_sheet_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        resin_type_id=resin_type_id,
    ).model_dump(mode="json")

    create_sheet_response = await client.post(
        url="/api/v1/production/production-sheets",
        json=payload,
    )
    assert create_sheet_response.status_code == 201, create_sheet_response.json()

    return create_sheet_response.json()


async def test_create_lab_test_through_api(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    created_sheet = await create_production_sheet(
        client, line_id, shift_id, resin_type_id
    )

    payload = build_lab_test_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        production_ref=created_sheet["production_ref"],
    ).model_dump(mode="json")

    response = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )

    body = response.json()

    assert response.status_code == 201, response.json()
    assert body["production_line_id"] == line_id
    assert body["shift_id"] == shift_id
    assert body["production_sheet_id"] == created_sheet["id"]


async def test_duplicate_lab_test_through_api_returns_conflict(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    created_sheet = await create_production_sheet(
        client, line_id, shift_id, resin_type_id
    )

    payload = build_lab_test_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        production_ref=created_sheet["production_ref"],
    ).model_dump(mode="json")

    first_response = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )
    assert first_response.status_code == 201, first_response.json()

    second_response = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )

    assert second_response.status_code == 409, second_response.json()


async def test_create_lab_test_through_api_missing_production_ref_returns_not_found(
    client,
):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)

    payload = build_lab_test_payload(
        production_line_id=create_line_response["id"],
        shift_id=create_shift_response["id"],
        production_ref=999,
    ).model_dump(mode="json")

    response = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )

    assert response.status_code == 404, response.json()


async def test_get_lab_test_through_api(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    created_sheet = await create_production_sheet(
        client, line_id, shift_id, resin_type_id
    )

    payload = build_lab_test_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        production_ref=created_sheet["production_ref"],
    ).model_dump(mode="json")

    new_lab_test = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )
    assert new_lab_test.status_code == 201, new_lab_test.json()

    created_lab_test_id = new_lab_test.json()["id"]

    response = await client.get(
        url=f"/api/v1/lab/lab-tests/{created_lab_test_id}",
    )

    body = response.json()

    assert response.status_code == 200, response.json()
    assert body["id"] == created_lab_test_id
    assert body["production_sheet_id"] == created_sheet["id"]


async def test_get_lab_test_through_api_returns_not_found(client):

    response = await client.get(
        url="/api/v1/lab/lab-tests/99",
    )

    assert response.status_code == 404, response.json()


async def test_list_lab_tests_through_api(client):

    create_line_response = await create_production_line(client)
    create_shift_response = await create_shift(client)
    create_resin_response = await create_resin_type(client)

    line_id = create_line_response["id"]
    shift_id = create_shift_response["id"]
    resin_type_id = create_resin_response["id"]

    created_sheet = await create_production_sheet(
        client, line_id, shift_id, resin_type_id
    )

    payload = build_lab_test_payload(
        production_line_id=line_id,
        shift_id=shift_id,
        production_ref=created_sheet["production_ref"],
    ).model_dump(mode="json")

    create_response = await client.post(
        url="/api/v1/lab/lab-tests",
        json=payload,
    )
    assert create_response.status_code == 201, create_response.json()

    response = await client.get(
        url="/api/v1/lab/lab-tests",
    )

    body = response.json()

    assert response.status_code == 200, response.json()
    assert len(body) == 1
    assert body[0]["production_sheet_id"] == created_sheet["id"]
