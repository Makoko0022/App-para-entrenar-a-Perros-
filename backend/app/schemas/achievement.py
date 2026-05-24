from datetime import datetime
from pydantic import BaseModel


class AchievementRead(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    xp_reward: int
    condition_type: str
    condition_value: int

    model_config = {"from_attributes": True}


class DogAchievementRead(BaseModel):
    id: int
    dog_id: int
    achievement: AchievementRead
    earned_at: datetime

    model_config = {"from_attributes": True}
