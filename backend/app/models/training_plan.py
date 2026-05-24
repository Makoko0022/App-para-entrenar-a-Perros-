from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TrainingPlan(Base):
    """Plan de entrenamiento personalizado para un perro."""
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=7)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    dog: Mapped["Dog"] = relationship(back_populates="training_plans")
    exercises: Mapped[list["PlanExercise"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="PlanExercise.order"
    )
    sessions: Mapped[list["TrainingSession"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<TrainingPlan id={self.id} name={self.name}>"


class PlanExercise(Base):
    """Ejercicio dentro de un plan de entrenamiento."""
    __tablename__ = "plan_exercises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("training_plans.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1)
    repetitions: Mapped[int] = mapped_column(Integer, default=5)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relaciones
    plan: Mapped["TrainingPlan"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(back_populates="plan_exercises")

    def __repr__(self) -> str:
        return f"<PlanExercise plan={self.plan_id} exercise={self.exercise_id}>"
