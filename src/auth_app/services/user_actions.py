from typing import TYPE_CHECKING

from sqlalchemy import RowMapping

from src.core.redis.cache_refresh_token import set_cache_refresh_token, get_cache_refresh_token
from src.core.redis.cache_decorator import async_set_get_cache
from src.auth_app.exceptions import UserHTTPException, AuthHTTPException
from src.auth_app.schemes.auth_schemes import AuthSchema
from src.auth_app.schemes.user_schemes import UserWorkSchema, UserUpdateSchema
from src.auth_app.services.password import password
from src.auth_app.services.token import app_token

if TYPE_CHECKING:
    from src.auth_app.services.user import CurrentUser
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi import Request


class AuthUserActions:

    async def login_user(self, request: "Request", user_input: AuthSchema, db: "AsyncSession") -> tuple[str, str]:

        user_instance = await password.verify_password(user_input=user_input, db=db)
        user = UserWorkSchema(**user_instance.__dict__)
        del user_input

        access_token: str = app_token.get_access_token(user)
        refresh_token: str = app_token.get_refresh_token(user)

        rc = request.app.state.redis_client
        await set_cache_refresh_token(cln=rc, username=user.username, token=refresh_token)

        return access_token, refresh_token

    async def logout_user(self, user: UserWorkSchema):
        pass

    async def refresh_login(self, request: "Request") -> tuple[str, str]:
        user = request.state.user.current_user
        rc = request.app.state.redis_client

        session_token: str = await get_cache_refresh_token(cln=rc, username=user.username)
        if not session_token or (session_token != request.state.token):
            AuthHTTPException.raise_http_403()

        access_token: str = app_token.get_access_token(user)
        refresh_token: str = app_token.get_refresh_token(user)

        await set_cache_refresh_token(cln=rc, username=user.username, token=refresh_token)

        return access_token, refresh_token


class UserActionsService:

    @async_set_get_cache(ttl=120, key="get_user")
    async def read_user(self, user: "CurrentUser") -> UserWorkSchema:
        """
        Чтение данных пользователя
        Args:
            user: instance of the class CurrentUser

        Returns: UserWorkSchema data
        """
        user_dict: RowMapping | None = await user.get_user_data()
        if user_dict is None:
            UserHTTPException.raise_http_404()

        response = UserWorkSchema.model_validate(user_dict)
        return response

    async def update_user(self, user: "CurrentUser", update_data: UserUpdateSchema) -> UserWorkSchema:
        """
        Изменение данных пользователя.
        Args:
            user: instance of the class CurrentUser
            update_data: data to update a user

        Returns: UserWorkSchema
        """

        user_dict: RowMapping = await user.update_user_data(update_data)
        if user_dict is None:
            UserHTTPException.raise_http_500()

        response = UserWorkSchema(**user_dict)
        return response

    async def delete_user(self, user: "CurrentUser") -> UserWorkSchema:
        """
        Удаление пользователя
        Args:
            user: instance of the class CurrentUser
        Returns:
        """
        user_check: RowMapping | None = await user.get_user_data()
        if user_check is None:
            UserHTTPException.raise_http_404()

        user_fields: RowMapping = await user.delete_user_data()
        if user_fields is None:
            UserHTTPException.raise_http_500()

        response = UserWorkSchema(**user_fields)
        return response
