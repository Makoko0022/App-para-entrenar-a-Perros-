from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.dog import Dog
from app.models.training_session import TrainingSession, SessionStatus
from app.models.achievement import Achievement, DogAchievement


async def check_and_award_achievements(dog: Dog, db: AsyncSession) -> list[Achievement]:
    """Verificar y otorgar logros según el progreso del perro."""
    awarded = []

    # Obtener logros activos
    achievements_result = await db.execute(
        select(Achievement).where(Achievement.is_active == True)
    )
    achievements = achievements_result.scalars().all()

    # Obtener logros ya ganados
    earned_result = await db.execute(
        select(DogAchievement.achievement_id).where(DogAchievement.dog_id == dog.id)
    )
    earned_ids = {row[0] for row in earned_result.all()}

    # Contar sesiones completadas
    sessions_result = await db.execute(
        select(func.count(TrainingSession.id)).where(
            TrainingSession.dog_id == dog.id,
            TrainingSession.status == SessionStatus.COMPLETADA
        )
    )
    sessions_count = sessions_result.scalar() or 0

    for achievement in achievements:
        if achievement.id in earned_ids:
            continue

        should_award = False
        if achievement.condition_type == "sessions_completed":
            should_award = sessions_count >= achievement.condition_value
        elif achievement.condition_type == "total_xp":
            should_award = dog.total_xp >= achievement.condition_value

        if should_award:
            dog_achievement = DogAchievement(
                dog_id=dog.id,
                achievement_id=achievement.id,
            )
            db.add(dog_achievement)
            dog.total_xp += achievement.xp_reward
            awarded.append(achievement)

    if awarded:
        await db.flush()

    return awarded
