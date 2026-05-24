from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class SessionStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class ExerciseResult(str, enum.Enum):
    EXCELENTE = "excelente"
    BIEN = "bien"
    REGULAR = "regular"
    MAL = "mal"
    OMITIDO = "omitido"


class TrainingSession(Base):
    """Sesión de entrenamiento registrada."""
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("training_plans.id"), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.PENDIENTE
    )
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)
    mood_score: Mapped[int] = mapped_column(Integer, nullable=True)  # 1-5 humor del perro
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    dog: Mapped["Dog"] = relationship(back_populates="training_sessions")
    plan: Mapped["TrainingPlan"] = relationship(back_populates="sessions")
    exercise_logs: Mapped[list["SessionExerciseLog"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TrainingSession id={self.id} dog={self.dog_id} status={self.status}>"


class SessionExerciseLog(Base):
    """Log de un ejercicio durante una sesión."""
    __tablename__ = "session_exercise_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    result: Mapped[ExerciseResult] = mapped_column(
        Enum(ExerciseResult), default=ExerciseResult.BIEN
    )
    repetitions_done: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    logged_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    session: Mapped["TrainingSession"] = relationship(back_populates="exercise_logs")
    exercise: Mapped["Exercise"] = relationship(back_populates="session_logs")

    def __repr__(self) -> str:
        return f"<SessionExerciseLog session={self.session_id} exercise={self.exercise_id}>"
