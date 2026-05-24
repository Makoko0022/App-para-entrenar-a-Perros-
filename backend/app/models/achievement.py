from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Achievement(Base):
    """Logro que puede ganar un perro."""
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=50)
    # Condición: ej. "sessions_completed:10", "exercises_mastered:5"
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    dog_achievements: Mapped[list["DogAchievement"]] = relationship(
        back_populates="achievement"
    )

    def __repr__(self) -> str:
        return f"<Achievement id={self.id} name={self.name}>"


class DogAchievement(Base):
    """Logro obtenido por un perro específico."""
    __tablename__ = "dog_achievements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relaciones
    dog: Mapped["Dog"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="dog_achievements")

    def __repr__(self) -> str:
        return f"<DogAchievement dog={self.dog_id} achievement={self.achievement_id}>"
