from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.dog import Dog
from app.models.training_plan import TrainingPlan, PlanExercise
from app.models.exercise import Exercise
from app.schemas.training_plan import (
    TrainingPlanCreate, TrainingPlanRead, TrainingPlanUpdate
)
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/dogs/{dog_id}/plans", tags=["Planes de Entrenamiento"])


async def get_dog_or_404(dog_id: int, user: User, db: AsyncSession) -> Dog:
    result = await db.execute(
        select(Dog).where(Dog.id == dog_id, Dog.owner_id == user.id)
    )
    dog = result.scalar_one_or_none()
    if not dog:
        raise HTTPException(status_code=404, detail="Perro no encontrado")
    return dog


@router.post("/", response_model=TrainingPlanRead, status_code=201)
async def create_plan(
    dog_id: int,
    plan_in: TrainingPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Crear un plan de entrenamiento para un perro."""
    await get_dog_or_404(dog_id, current_user, db)

    plan = TrainingPlan(
        dog_id=dog_id,
        name=plan_in.name,
        description=plan_in.description,
        duration_days=plan_in.duration_days,
    )
    db.add(plan)
    await db.flush()

    # Agregar ejercicios al plan
    for ex_data in plan_in.exercises:
        # Verificar que el ejercicio existe
        ex_result = await db.execute(
            select(Exercise).where(Exercise.id == ex_data.exercise_id)
        )
        if not ex_result.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"Ejercicio {ex_data.exercise_id} no encontrado"
            )
        plan_ex = PlanExercise(plan_id=plan.id, **ex_data.model_dump())
        db.add(plan_ex)

    await db.flush()
    # Recargar con relaciones
    result = await db.execute(
        select(TrainingPlan)
        .options(selectinload(TrainingPlan.exercises).selectinload(PlanExercise.exercise))
        .where(TrainingPlan.id == plan.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[TrainingPlanRead])
async def list_plans(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar planes de entrenamiento de un perro."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingPlan)
        .options(selectinload(TrainingPlan.exercises).selectinload(PlanExercise.exercise))
        .where(TrainingPlan.dog_id == dog_id)
        .order_by(TrainingPlan.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{plan_id}", response_model=TrainingPlanRead)
async def get_plan(
    dog_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener un plan de entrenamiento."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingPlan)
        .options(selectinload(TrainingPlan.exercises).selectinload(PlanExercise.exercise))
        .where(TrainingPlan.id == plan_id, TrainingPlan.dog_id == dog_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


@router.patch("/{plan_id}", response_model=TrainingPlanRead)
async def update_plan(
    dog_id: int,
    plan_id: int,
    plan_update: TrainingPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar un plan de entrenamiento."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingPlan).where(TrainingPlan.id == plan_id, TrainingPlan.dog_id == dog_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    await db.flush()

    result = await db.execute(
        select(TrainingPlan)
        .options(selectinload(TrainingPlan.exercises).selectinload(PlanExercise.exercise))
        .where(TrainingPlan.id == plan.id)
    )
    return result.scalar_one()


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    dog_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar un plan de entrenamiento."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingPlan).where(TrainingPlan.id == plan_id, TrainingPlan.dog_id == dog_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    await db.delete(plan)
