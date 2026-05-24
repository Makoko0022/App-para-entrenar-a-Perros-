import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_dog(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/dogs/", json={
        "name": "Buddy",
        "breed": "Labrador",
        "gender": "macho",
        "size": "grande",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Buddy"
    assert data["breed"] == "Labrador"
    assert data["total_xp"] == 0
    assert data["training_level"] == "principiante"


@pytest.mark.asyncio
async def test_list_dogs(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/dogs/", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_update_dog(client: AsyncClient, auth_headers: dict):
    # Crear perro
    create_resp = await client.post("/api/v1/dogs/", json={
        "name": "Max",
        "breed": "Poodle",
    }, headers=auth_headers)
    dog_id = create_resp.json()["id"]

    # Actualizar
    resp = await client.patch(f"/api/v1/dogs/{dog_id}", json={
        "name": "Maxi",
        "weight_kg": 5.5,
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Maxi"


@pytest.mark.asyncio
async def test_get_dog_stats(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/v1/dogs/", json={"name": "Luna"}, headers=auth_headers)
    dog_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/dogs/{dog_id}/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["dog_name"] == "Luna"
    assert data["total_sessions"] == 0


@pytest.mark.asyncio
async def test_delete_dog(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/v1/dogs/", json={"name": "Temporal"}, headers=auth_headers)
    dog_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/dogs/{dog_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/dogs/{dog_id}", headers=auth_headers)
    assert resp.status_code == 404
