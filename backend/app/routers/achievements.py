from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.dog import Dog
from app.models.achievement import Achievement, DogAchievement
from app.schemas.achievement import AchievementRead, DogAchievementRead
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["Logros"])


@router.get("/achievements", response_model=list[AchievementRead])
async def list_achievements(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Listar todos los logros disponibles."""
    result = await db.execute(
        select(Achievement).where(Achievement.is_active == True)
    )
    return result.scalars().all()


@router.get("/dogs/{dog_id}/achievements", response_model=list[DogAchievementRead])
async def get_dog_achievements(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener logros obtenidos por un perro."""
    dog_result = await db.execute(
        select(Dog).where(Dog.id == dog_id, Dog.owner_id == current_user.id)
    )
    if not dog_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Perro no encontrado")

    result = await db.execute(
        select(DogAchievement)
        .options(selectinload(DogAchievement.achievement))
        .where(DogAchievement.dog_id == dog_id)
        .order_by(DogAchievement.earned_at.desc())
    )
    return result.scalars().all()
