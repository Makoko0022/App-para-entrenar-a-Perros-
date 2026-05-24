from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Obtener perfil del usuario actual."""
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar perfil del usuario actual."""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user
