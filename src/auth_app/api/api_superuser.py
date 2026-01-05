from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.repositories.superuser_repository import SuperuserRepo
from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.schemes.user_schemes import UserWorkSchema, UsersAllSchema
from src.auth_app.services.auth import authenticate, available_admin


@router.get(
    path="/users",
    status_code=status.HTTP_200_OK,
    response_model=UsersAllSchema,
    dependencies=[Depends(authenticate), Depends(available_admin)]
)
async def get_all_users(limit: int = 10, db: AsyncSession = Depends(get_async_db)) -> UsersAllSchema:
    """
    Отдаёт данные о всех зарегистрированных пользователях
    """
    users = await SuperuserRepo.select_users(db)
    response = UsersAllSchema(users=[UserWorkSchema.model_validate(user) for user in users])
    return response

