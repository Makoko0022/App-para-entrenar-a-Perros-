import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_exercises(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/exercises/", headers=auth_headers)
    assert resp.status_code == 200
    exercises = resp.json()
    assert len(exercises) > 0
    assert exercises[0]["name"] is not None


@pytest.mark.asyncio
async def test_filter_exercises_by_category(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/exercises/?category=básico", headers=auth_headers)
    assert resp.status_code == 200
    for ex in resp.json():
        assert ex["category"] == "básico"


@pytest.mark.asyncio
async def test_create_training_plan(client: AsyncClient, auth_headers: dict):
    # Crear perro
    dog_resp = await client.post("/api/v1/dogs/", json={"name": "Rex"}, headers=auth_headers)
    dog_id = dog_resp.json()["id"]

    # Obtener ejercicios disponibles
    ex_resp = await client.get("/api/v1/exercises/", headers=auth_headers)
    ex_id = ex_resp.json()[0]["id"]

    # Crear plan
    resp = await client.post(f"/api/v1/dogs/{dog_id}/plans/", json={
        "name": "Plan Básico",
        "description": "Plan de 7 días para principiantes",
        "duration_days": 7,
        "exercises": [{"exercise_id": ex_id, "order": 1, "repetitions": 5}]
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Plan Básico"
    assert len(data["exercises"]) == 1


@pytest.mark.asyncio
async def test_training_session_flow(client: AsyncClient, auth_headers: dict):
    """Test del flujo completo: crear sesión → registrar ejercicio → completar."""
    # Crear perro
    dog_resp = await client.post("/api/v1/dogs/", json={"name": "Bella"}, headers=auth_headers)
    dog_id = dog_resp.json()["id"]

    # Obtener ejercicio
    ex_resp = await client.get("/api/v1/exercises/", headers=auth_headers)
    ex_id = ex_resp.json()[0]["id"]

    # Iniciar sesión
    session_resp = await client.post(f"/api/v1/dogs/{dog_id}/sessions/", json={
        "notes": "Primera sesión de prueba"
    }, headers=auth_headers)
    assert session_resp.status_code == 201
    session_id = session_resp.json()["id"]
    assert session_resp.json()["status"] == "en_progreso"

    # Registrar ejercicio
    log_resp = await client.post(
        f"/api/v1/dogs/{dog_id}/sessions/{session_id}/exercises",
        json={"exercise_id": ex_id, "result": "bien", "repetitions_done": 5},
        headers=auth_headers
    )
    assert log_resp.status_code == 201
    assert log_resp.json()["xp_earned"] > 0

    # Completar sesión
    complete_resp = await client.post(
        f"/api/v1/dogs/{dog_id}/sessions/{session_id}/complete",
        json={"mood_score": 5},
        headers=auth_headers
    )
    assert complete_resp.status_code == 200
    data = complete_resp.json()
    assert data["status"] == "completada"
    assert data["xp_earned"] > 0

    # Verificar que el perro ganó XP
    dog_resp = await client.get(f"/api/v1/dogs/{dog_id}", headers=auth_headers)
    assert dog_resp.json()["total_xp"] > 0


@pytest.mark.asyncio
async def test_list_achievements(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/achievements", headers=auth_headers)
    assert resp.status_code == 200
    achievements = resp.json()
    assert len(achievements) > 0
