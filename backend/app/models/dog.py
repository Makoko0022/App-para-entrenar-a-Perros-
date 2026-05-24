from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Integer, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class DogSize(str, enum.Enum):
    PEQUEÑO = "pequeño"
    MEDIANO = "mediano"
    GRANDE = "grande"
    GIGANTE = "gigante"


class DogGender(str, enum.Enum):
    MACHO = "macho"
    HEMBRA = "hembra"


class TrainingLevel(str, enum.Enum):
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"


class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    breed: Mapped[str] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    gender: Mapped[DogGender] = mapped_column(
        Enum(DogGender), default=DogGender.MACHO, nullable=False
    )
    size: Mapped[DogSize] = mapped_column(
        Enum(DogSize), default=DogSize.MEDIANO, nullable=False
    )
    weight_kg: Mapped[float] = mapped_column(nullable=True)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    training_level: Mapped[TrainingLevel] = mapped_column(
        Enum(TrainingLevel), default=TrainingLevel.PRINCIPIANTE
    )
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relaciones
    owner: Mapped["User"] = relationship(back_populates="dogs")
    training_sessions: Mapped[list["TrainingSession"]] = relationship(
        back_populates="dog", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["DogAchievement"]] = relationship(
        back_populates="dog", cascade="all, delete-orphan"
    )
    training_plans: Mapped[list["TrainingPlan"]] = relationship(
        back_populates="dog", cascade="all, delete-orphan"
    )

    @property
    def age_months(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        return (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)

    def __repr__(self) -> str:
        return f"<Dog id={self.id} name={self.name}>"
