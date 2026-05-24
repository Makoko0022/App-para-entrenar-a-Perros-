from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.dog import Dog, TrainingLevel
from app.models.exercise import Exercise
from app.models.training_session import TrainingSession, SessionStatus, SessionExerciseLog
from app.schemas.training_session import (
    StartSession, TrainingSessionRead, TrainingSessionUpdate,
    SessionExerciseLogCreate, SessionExerciseLogRead
)
from app.services.achievement_service import check_and_award_achievements
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/dogs/{dog_id}/sessions", tags=["Sesiones de Entrenamiento"])


async def get_dog_or_404(dog_id: int, user: User, db: AsyncSession) -> Dog:
    result = await db.execute(
        select(Dog).where(Dog.id == dog_id, Dog.owner_id == user.id)
    )
    dog = result.scalar_one_or_none()
    if not dog:
        raise HTTPException(status_code=404, detail="Perro no encontrado")
    return dog


@router.post("/", response_model=TrainingSessionRead, status_code=201)
async def start_session(
    dog_id: int,
    session_in: StartSession,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Iniciar una nueva sesión de entrenamiento."""
    await get_dog_or_404(dog_id, current_user, db)

    session = TrainingSession(
        dog_id=dog_id,
        plan_id=session_in.plan_id,
        notes=session_in.notes,
        status=SessionStatus.EN_PROGRESO,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()

    result = await db.execute(
        select(TrainingSession)
        .options(selectinload(TrainingSession.exercise_logs))
        .where(TrainingSession.id == session.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[TrainingSessionRead])
async def list_sessions(
    dog_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar sesiones de un perro."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingSession)
        .options(selectinload(TrainingSession.exercise_logs))
        .where(TrainingSession.dog_id == dog_id)
        .order_by(TrainingSession.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=TrainingSessionRead)
async def get_session(
    dog_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener una sesión de entrenamiento."""
    await get_dog_or_404(dog_id, current_user, db)
    result = await db.execute(
        select(TrainingSession)
        .options(selectinload(TrainingSession.exercise_logs))
        .where(TrainingSession.id == session_id, TrainingSession.dog_id == dog_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.post("/{session_id}/exercises", response_model=SessionExerciseLogRead, status_code=201)
async def log_exercise(
    dog_id: int,
    session_id: int,
    log_in: SessionExerciseLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Registrar el resultado de un ejercicio en la sesión."""
    await get_dog_or_404(dog_id, current_user, db)

    # Verificar sesión
    session_result = await db.execute(
        select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.dog_id == dog_id,
            TrainingSession.status == SessionStatus.EN_PROGRESO
        )
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión activa no encontrada")

    # Verificar ejercicio
    ex_result = await db.execute(select(Exercise).where(Exercise.id == log_in.exercise_id))
    exercise = ex_result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    # Calcular XP según resultado
    xp_multipliers = {"excelente": 1.5, "bien": 1.0, "regular": 0.5, "mal": 0.0, "omitido": 0.0}
    xp = int(exercise.xp_reward * xp_multipliers.get(log_in.result.value, 1.0))

    log = SessionExerciseLog(
        session_id=session_id,
        xp_earned=xp,
        **log_in.model_dump(),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.post("/{session_id}/complete", response_model=TrainingSessionRead)
async def complete_session(
    dog_id: int,
    session_id: int,
    update_data: TrainingSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Completar una sesión de entrenamiento."""
    dog = await get_dog_or_404(dog_id, current_user, db)

    session_result = await db.execute(
        select(TrainingSession)
        .options(selectinload(TrainingSession.exercise_logs))
        .where(TrainingSession.id == session_id, TrainingSession.dog_id == dog_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    if session.status == SessionStatus.COMPLETADA:
        raise HTTPException(status_code=400, detail="La sesión ya está completada")

    now = datetime.now(timezone.utc)
    session.status = SessionStatus.COMPLETADA
    session.completed_at = now
    if update_data.notes:
        session.notes = update_data.notes
    if update_data.mood_score:
        session.mood_score = update_data.mood_score

    # Calcular duración y XP total
    if session.started_at:
        started = session.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        duration = (now - started).total_seconds() / 60
        session.duration_minutes = round(duration, 2)

    total_xp = sum(log.xp_earned for log in session.exercise_logs)
    session.xp_earned = total_xp

    # Actualizar XP del perro y nivel
    dog.total_xp += total_xp
    _update_training_level(dog)

    await db.flush()

    # Verificar y otorgar logros
    await check_and_award_achievements(dog, db)

    result = await db.execute(
        select(TrainingSession)
        .options(selectinload(TrainingSession.exercise_logs))
        .where(TrainingSession.id == session.id)
    )
    return result.scalar_one()


def _update_training_level(dog: Dog) -> None:
    """Actualiza el nivel de entrenamiento según el XP total."""
    if dog.total_xp >= 1000:
        dog.training_level = TrainingLevel.AVANZADO
    elif dog.total_xp >= 300:
        dog.training_level = TrainingLevel.INTERMEDIO
    else:
        dog.training_level = TrainingLevel.PRINCIPIANTE
