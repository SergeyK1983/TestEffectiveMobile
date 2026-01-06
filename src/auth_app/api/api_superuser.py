from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.exceptions import UserHTTPException
from src.auth_app.repositories.superuser_repository import SuperuserRepo
from src.auth_app.schemes.user_schemes import UserWorkSchema, UsersAllSchema, UserServiceFieldsSchema
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


@router.post(
    path="/set_service_fields_user",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate), Depends(available_admin)]
)
async def set_service_fields_user(body: UserServiceFieldsSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Изменение администратором сервисных полей пользователя.
    """
    username = body.username
    data = body.model_dump(exclude_none=True)

    user = await SuperuserRepo.is_unique_user(username=username, email=None, db=db)
    if not user:
        UserHTTPException.raise_http_404()

    data_returning = await SuperuserRepo.update_user_by_admin(username, data, db)
    return data_returning
