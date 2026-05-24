from datetime import datetime, date
from pydantic import BaseModel, field_validator
from app.models.dog import DogSize, DogGender, TrainingLevel


class DogCreate(BaseModel):
    name: str
    breed: str | None = None
    birth_date: date | None = None
    gender: DogGender = DogGender.MACHO
    size: DogSize = DogSize.MEDIANO
    weight_kg: float | None = None
    photo_url: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class DogUpdate(BaseModel):
    name: str | None = None
    breed: str | None = None
    birth_date: date | None = None
    gender: DogGender | None = None
    size: DogSize | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    training_level: TrainingLevel | None = None
    notes: str | None = None


class DogRead(BaseModel):
    id: int
    owner_id: int
    name: str
    breed: str | None
    birth_date: date | None
    gender: DogGender
    size: DogSize
    weight_kg: float | None
    photo_url: str | None
    training_level: TrainingLevel
    notes: str | None
    total_xp: int
    age_months: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DogStats(BaseModel):
    dog_id: int
    dog_name: str
    total_sessions: int
    completed_sessions: int
    total_xp: int
    training_level: TrainingLevel
    achievements_count: int
    last_session_date: datetime | None

    model_config = {"from_attributes": True}
