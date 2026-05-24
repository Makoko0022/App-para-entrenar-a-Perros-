from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.training_session import SessionStatus, ExerciseResult


class SessionExerciseLogCreate(BaseModel):
    exercise_id: int
    result: ExerciseResult = ExerciseResult.BIEN
    repetitions_done: int = 0
    duration_seconds: int | None = None
    notes: str | None = None


class SessionExerciseLogRead(BaseModel):
    id: int
    exercise_id: int
    result: ExerciseResult
    repetitions_done: int
    duration_seconds: int | None
    notes: str | None
    xp_earned: int
    logged_at: datetime

    model_config = {"from_attributes": True}


class TrainingSessionCreate(BaseModel):
    plan_id: int | None = None
    notes: str | None = None


class StartSession(BaseModel):
    """Iniciar una sesión con un conjunto de ejercicios."""
    plan_id: int | None = None
    notes: str | None = None


class TrainingSessionUpdate(BaseModel):
    status: SessionStatus | None = None
    notes: str | None = None
    mood_score: int | None = None

    @field_validator("mood_score")
    @classmethod
    def validate_mood(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("El mood_score debe estar entre 1 y 5")
        return v


class TrainingSessionRead(BaseModel):
    id: int
    dog_id: int
    plan_id: int | None
    status: SessionStatus
    duration_minutes: float | None
    xp_earned: int
    notes: str | None
    mood_score: int | None
    started_at: datetime | None
    completed_at: datetime | None
    exercise_logs: list[SessionExerciseLogRead]
    created_at: datetime

    model_config = {"from_attributes": True}
