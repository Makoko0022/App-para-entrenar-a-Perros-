from datetime import datetime
from pydantic import BaseModel
from app.models.exercise import ExerciseCategory, DifficultyLevel


class ExerciseCreate(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    category: ExerciseCategory = ExerciseCategory.BASICO
    difficulty: DifficultyLevel = DifficultyLevel.FACIL
    duration_seconds: int = 60
    xp_reward: int = 10
    icon: str | None = None
    video_url: str | None = None


class ExerciseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    category: ExerciseCategory | None = None
    difficulty: DifficultyLevel | None = None
    duration_seconds: int | None = None
    xp_reward: int | None = None
    icon: str | None = None
    video_url: str | None = None
    is_active: bool | None = None


class ExerciseRead(BaseModel):
    id: int
    name: str
    description: str | None
    instructions: str | None
    category: ExerciseCategory
    difficulty: DifficultyLevel
    duration_seconds: int
    xp_reward: int
    icon: str | None
    video_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
