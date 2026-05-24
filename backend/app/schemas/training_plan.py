from datetime import datetime
from pydantic import BaseModel
from app.schemas.exercise import ExerciseRead


class PlanExerciseCreate(BaseModel):
    exercise_id: int
    order: int = 1
    repetitions: int = 5
    duration_seconds: int | None = None
    notes: str | None = None


class PlanExerciseRead(BaseModel):
    id: int
    exercise_id: int
    order: int
    repetitions: int
    duration_seconds: int | None
    notes: str | None
    exercise: ExerciseRead

    model_config = {"from_attributes": True}


class TrainingPlanCreate(BaseModel):
    name: str
    description: str | None = None
    duration_days: int = 7
    exercises: list[PlanExerciseCreate] = []


class TrainingPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_days: int | None = None
    is_active: bool | None = None


class TrainingPlanRead(BaseModel):
    id: int
    dog_id: int
    name: str
    description: str | None
    duration_days: int
    is_active: bool
    exercises: list[PlanExerciseRead]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
