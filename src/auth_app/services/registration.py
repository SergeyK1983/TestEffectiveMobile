from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.exceptions import UserHTTPException
from src.auth_app.repositories import UserRegisterRepo, UserRegisteredRepo
from src.auth_app.schemes.user_schemes import UserRegisterSchema, UserWorkSchema
from src.auth_app.services.password import password


class RegistrationService:

    def __init__(self, user: UserRegisterSchema, db: AsyncSession):
        self.user: UserRegisterSchema = user
        self.user.password = password.hashing_password(self.user.password)
        self.db_session: AsyncSession = db

    async def create_user(self) -> UserWorkSchema:
        """
        Создание пользователя.
        Returns:
            UserWorkSchema data
        """
        user_exists = await UserRegisteredRepo.is_unique_user(
            username=self.user.username, email=self.user.email, db=self.db_session
        )
        if user_exists:
            UserHTTPException.raise_http_409()

        user_fields: RowMapping = await UserRegisterRepo.create_user(self.user, self.db_session)
        if user_fields is None:
            UserHTTPException.raise_http_500()

        response = UserWorkSchema(**user_fields)
        return response
