from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.dog import Dog
from app.models.training_session import TrainingSession, SessionStatus
from app.models.achievement import DogAchievement
from app.schemas.dog import DogCreate, DogRead, DogUpdate, DogStats
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/dogs", tags=["Perros"])


async def get_dog_or_404(dog_id: int, user: User, db: AsyncSession) -> Dog:
    result = await db.execute(
        select(Dog).where(Dog.id == dog_id, Dog.owner_id == user.id)
    )
    dog = result.scalar_one_or_none()
    if not dog:
        raise HTTPException(status_code=404, detail="Perro no encontrado")
    return dog


@router.post("/", response_model=DogRead, status_code=201)
async def create_dog(
    dog_in: DogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Registrar un nuevo perro."""
    dog = Dog(**dog_in.model_dump(), owner_id=current_user.id)
    db.add(dog)
    await db.flush()
    await db.refresh(dog)
    return dog


@router.get("/", response_model=list[DogRead])
async def list_dogs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar todos los perros del usuario."""
    result = await db.execute(select(Dog).where(Dog.owner_id == current_user.id))
    return result.scalars().all()


@router.get("/{dog_id}", response_model=DogRead)
async def get_dog(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener un perro por ID."""
    return await get_dog_or_404(dog_id, current_user, db)


@router.patch("/{dog_id}", response_model=DogRead)
async def update_dog(
    dog_id: int,
    dog_update: DogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar datos de un perro."""
    dog = await get_dog_or_404(dog_id, current_user, db)
    update_data = dog_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dog, field, value)
    await db.flush()
    await db.refresh(dog)
    return dog


@router.delete("/{dog_id}", status_code=204)
async def delete_dog(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar un perro."""
    dog = await get_dog_or_404(dog_id, current_user, db)
    await db.delete(dog)


@router.get("/{dog_id}/stats", response_model=DogStats)
async def get_dog_stats(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener estadísticas de entrenamiento de un perro."""
    dog = await get_dog_or_404(dog_id, current_user, db)

    # Total sesiones
    total_result = await db.execute(
        select(func.count(TrainingSession.id)).where(TrainingSession.dog_id == dog_id)
    )
    total_sessions = total_result.scalar() or 0

    # Sesiones completadas
    completed_result = await db.execute(
        select(func.count(TrainingSession.id)).where(
            TrainingSession.dog_id == dog_id,
            TrainingSession.status == SessionStatus.COMPLETADA
        )
    )
    completed_sessions = completed_result.scalar() or 0

    # Logros
    achievements_result = await db.execute(
        select(func.count(DogAchievement.id)).where(DogAchievement.dog_id == dog_id)
    )
    achievements_count = achievements_result.scalar() or 0

    # Última sesión
    last_session_result = await db.execute(
        select(TrainingSession.completed_at)
        .where(
            TrainingSession.dog_id == dog_id,
            TrainingSession.status == SessionStatus.COMPLETADA
        )
        .order_by(TrainingSession.completed_at.desc())
        .limit(1)
    )
    last_session_date = last_session_result.scalar_one_or_none()

    return DogStats(
        dog_id=dog.id,
        dog_name=dog.name,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_xp=dog.total_xp,
        training_level=dog.training_level,
        achievements_count=achievements_count,
        last_session_date=last_session_date,
    )
