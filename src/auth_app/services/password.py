from typing import TYPE_CHECKING
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError, VerificationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping

from src.core.logger import logger
from src.auth_app.exceptions import AuthHTTPException, UserHTTPException
from src.auth_app.schemes.auth_schemes import AuthSchema
from src.auth_app.repositories import UserPasswordRepo
from src.auth_app.schemes.user_schemes import ChangePasswordSchema, UserWorkSchema

if TYPE_CHECKING:
    from src.auth_app.models import CustomUser
    from src.auth_app.services.user import CurrentUser


ph = PasswordHasher()


def get_hasher() -> PasswordHasher:
    return ph


class Password:

    @classmethod
    def hashing_password(cls, pwd: str) -> str:
        try:
            hash_pwd = get_hasher().hash(password=pwd)
        except HashingError as exp:
            logger.error("Хеширование не удалось: {}", exp.args[0])
            UserHTTPException.raise_http_500()
        return hash_pwd

    async def verify_password(self, user_input: AuthSchema, db: AsyncSession) -> "CustomUser":
        user_instance = await UserPasswordRepo.read_user_with_password(
            user_input.username, user_input.email, db
        )
        if not user_instance:
            AuthHTTPException.raise_http_401()
        try:
            get_hasher().verify(user_instance.password, user_input.password)
        except (VerifyMismatchError, VerificationError) as exp:
            logger.info("Проверка пароля: {}", exp.args[0])
            AuthHTTPException.raise_http_401()

        await self._check_rehash_password(user_input.password, user_instance.password, user_instance.id, db)
        user_instance.password = ""
        return user_instance

    async def _check_rehash_password(self, pwd: str, hashed_pwd: str, user_id: UUID, db: AsyncSession) -> None:
        if get_hasher().check_needs_rehash(hashed_pwd):
            new_hash_pwd = self.hashing_password(pwd)
            user_returning = await UserPasswordRepo.update_user_password(
                user_id=user_id,
                password=new_hash_pwd,
                db=db
            )
            if user_returning is None:
                UserHTTPException.raise_http_500()
        return

    async def change_password(self, user_id: UUID, pwd: str, db: AsyncSession) -> RowMapping | None:
        """
        Смена пароля
        Args:
            user_id: идентификатор пользователя
            pwd: новый хэшированный пароль
            db: async session
        Returns:
            id, username from returning row
        """
        user_returning: RowMapping = await UserPasswordRepo.update_user_password(
            user_id=user_id,
            password=pwd,
            db=db
        )
        return user_returning

    def reset_password(self) -> bool: ...


password = Password()


class ChangePasswordService:

    def __init__(self, user: "CurrentUser", pwd: ChangePasswordSchema):
        self.pwd_old: str = pwd.old_password
        self.pwd_new_hash: str = password.hashing_password(pwd.new_password)
        self.user: "CurrentUser" = user

    async def update_current_password(self):
        """
        Смена текущего пароля пользователя
        """

        auth = AuthSchema(username=self.user.current_user.username, password=self.pwd_old)
        await password.verify_password(auth, self.user.db_session)

        user_fields: RowMapping = await password.change_password(
            user_id=self.user.current_user.id,
            pwd=self.pwd_new_hash,
            db=self.user.db_session
        )
        if user_fields is None:
            UserHTTPException.raise_http_500()

        response = UserWorkSchema(**user_fields)
        return response

