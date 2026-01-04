from typing import TYPE_CHECKING

from sqlalchemy import RowMapping

from src.auth_app.exceptions import UserHTTPException
from src.auth_app.schemes.auth_schemes import AuthSchema
from src.auth_app.schemes.user_schemes import UserWorkSchema, UserUpdateSchema
from src.auth_app.services.password import password
from src.auth_app.services.token import app_token

if TYPE_CHECKING:
    from src.auth_app.services.user import CurrentUser
    from sqlalchemy.ext.asyncio import AsyncSession


class AuthUserActions:

    async def login_user(self, user_input: AuthSchema, db: "AsyncSession") -> tuple[str, str]:

        user_instance = await password.verify_password(user_input=user_input, db=db)
        user = UserWorkSchema(**user_instance.__dict__)
        del user_input

        access_token: str = app_token.get_access_token(user)
        refresh_token: str = app_token.get_refresh_token(user)
        return access_token, refresh_token

    async def logout_user(self, user: UserWorkSchema):
        pass


class UserActionsService:

    async def read_user(self, user: "CurrentUser") -> UserWorkSchema | None:
        """
        Чтение данных пользователя
        Args:
            user: instance of the class CurrentUser

        Returns: UserWorkSchema data
        """
        user_dict: dict | None = await user.get_user_data()
        if user_dict is None:
            UserHTTPException.raise_http_404()

        response = UserWorkSchema(**user_dict)
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
        user_check: dict | None = await user.get_user_data()
        if user_check is None:
            UserHTTPException.raise_http_404()

        user_fields: RowMapping = await user.delete_user_data()
        if user_fields is None:
            UserHTTPException.raise_http_500()

        response = UserWorkSchema(**user_fields)
        return response
