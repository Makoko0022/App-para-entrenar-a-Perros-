from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Boolean, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class ExerciseCategory(str, enum.Enum):
    BASICO = "básico"
    OBEDIENCIA = "obediencia"
    AGILIDAD = "agilidad"
    TRUCOS = "trucos"
    SOCIALIZACION = "socialización"
    COMPORTAMIENTO = "comportamiento"


class DifficultyLevel(str, enum.Enum):
    FACIL = "fácil"
    MEDIO = "medio"
    DIFICIL = "difícil"


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    instructions: Mapped[str] = mapped_column(String(5000), nullable=True)
    category: Mapped[ExerciseCategory] = mapped_column(
        Enum(ExerciseCategory), default=ExerciseCategory.BASICO
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel), default=DifficultyLevel.FACIL
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, default=60)
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    plan_exercises: Mapped[list["PlanExercise"]] = relationship(back_populates="exercise")
    session_logs: Mapped[list["SessionExerciseLog"]] = relationship(back_populates="exercise")

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name={self.name}>"
