from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Request, Depends, status

from src.core.database import get_async_db
from src.auth_app.api import router
from src.auth_app.exceptions import AuthHTTPException
from src.auth_app.schemes.user_schemes import UserWorkSchema, UserUpdateSchema
from src.auth_app.services.auth import authenticate
from src.auth_app.services.user_actions import UserActionsService

if TYPE_CHECKING:
    from src.auth_app.services.user import CurrentUser


@router.delete(
    path="/remove_user/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate), Depends(get_async_db)]
)
async def delete_user(request: Request, user_id: UUID):
    """
    Удаление пользователя из системы.
    Args:
        request: Request
        user_id: id of the user
        db: session
    Returns:
        msg and User deleted
    """
    user: "CurrentUser" = request.state.user
    if user.current_user.id != user_id:
        AuthHTTPException.raise_http_403()

    response: UserWorkSchema = await UserActionsService().delete_user(user=user)
    return {"msg": f"Пользователь {response.username} удален!"}


@router.get(
    path="/user_info/{user_id}",
    response_model=UserWorkSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate), Depends(get_async_db)]
)
async def get_user_data(request: Request, user_id: UUID):
    """
    Получает основные данные пользователя
    Args:
        request: Request
        user_id: id of the user
    Returns:
        info of the user
    """
    user: "CurrentUser" = request.state.user
    if user.current_user.id != user_id:
        AuthHTTPException.raise_http_403()

    user_data: UserWorkSchema | dict = await UserActionsService().read_user(user)
    return user_data


@router.post(
    path="/update_user/{user_id}",
    response_model=UserWorkSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate), Depends(get_async_db)]
)
async def update_user_data(request: Request, user_data: UserUpdateSchema, user_id: UUID):
    """
    Обновляет данные пользователя, которые переданы в запросе.
    Args:
        request: Request
        user_id: id of the user
        user_data: data of the user to update
        db: session
    Returns:
        info of the user
    """
    user: "CurrentUser" = request.state.user
    if user.current_user.id != user_id:
        AuthHTTPException.raise_http_403()

    user: UserWorkSchema = await UserActionsService().update_user(user=user, update_data=user_data)
    return user
