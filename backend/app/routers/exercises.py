from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.exercise import Exercise, ExerciseCategory, DifficultyLevel
from app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/exercises", tags=["Ejercicios"])


@router.get("/", response_model=list[ExerciseRead])
async def list_exercises(
    category: ExerciseCategory | None = Query(None),
    difficulty: DifficultyLevel | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Listar ejercicios de la biblioteca (con filtros opcionales)."""
    query = select(Exercise).where(Exercise.is_active == True)
    if category:
        query = query.where(Exercise.category == category)
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
    result = await db.execute(query.order_by(Exercise.category, Exercise.difficulty))
    return result.scalars().all()


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Obtener un ejercicio por ID."""
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    return exercise


@router.post("/", response_model=ExerciseRead, status_code=201)
async def create_exercise(
    exercise_in: ExerciseCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Crear un nuevo ejercicio en la biblioteca."""
    exercise = Exercise(**exercise_in.model_dump())
    db.add(exercise)
    await db.flush()
    await db.refresh(exercise)
    return exercise


@router.patch("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Actualizar un ejercicio."""
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    update_data = exercise_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    await db.flush()
    await db.refresh(exercise)
    return exercise
