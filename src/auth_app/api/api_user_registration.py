from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Request, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.schemes.user_schemes import UserRegisterSchema, ChangePasswordSchema
from src.auth_app.services.auth import authenticate
from src.auth_app.services.password import ChangePasswordService
from src.auth_app.services.registration import RegistrationService
from src.auth_app.exceptions import AuthHTTPException

if TYPE_CHECKING:
    from src.auth_app.services.user import CurrentUser


@router.post(path="/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegisterSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
    Args:
        user: schema UserRegister
        db: session
    Returns:
        msg and schema User
    """
    response = await RegistrationService(user, db).create_user()
    return response


@router.post(
    path="/change-password/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate)]
)
async def change_password(
        request: Request, user_id: UUID, password: ChangePasswordSchema, db: AsyncSession = Depends(get_async_db)
):
    """
    Смена пароля пользователя.
    Args:
        request: Request
        user_id: id of the user
        password: data for change password
        db: session
    """
    user: "CurrentUser" = request.state.user
    if user.current_user.id != user_id:
        AuthHTTPException.raise_http_403()

    if password.new_password != password.repeat_password:
        AuthHTTPException.raise_http_400()

    response = await ChangePasswordService(user, password).update_current_password()
    return {"msg": f"Пароль пользователя {response.username} изменён."}
