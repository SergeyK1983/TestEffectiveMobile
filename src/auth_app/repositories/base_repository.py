from uuid import UUID

from sqlalchemy import select, String, Select, or_, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.models import CustomUser
from src.core.logger import logger


class UserBaseRepo:

    @staticmethod
    def _select_user_fields() -> Select:
        """ Основные данные пользователя для работы с ними """

        query = select(
            CustomUser.id,
            CustomUser.username,
            CustomUser.email,
            CustomUser.first_name,
            CustomUser.second_name,
            CustomUser.last_name,
            CustomUser.is_active,
            CustomUser.is_staff,
            CustomUser.is_superuser,
        )
        return query

    @staticmethod
    async def _select_execute_query(query: Select, db: AsyncSession):
        """ Select запрос в БД """
        try:
            result = await db.execute(query)
        except IntegrityError as exp:
            logger.error("Ошибка чтения данных пользователя из БД {}", exp)
            return
        return result

    @classmethod
    async def _is_exists_user_by_username(cls, username: str, db: AsyncSession) -> bool:
        query = select(exists().where(CustomUser.username.cast(String) == username))
        try:
            result: bool = await db.scalar(query)
        except IntegrityError as exp:
            logger.error("Ошибка чтения БД при проверке пользователя {}", exp)
            result = True

        return result

    @classmethod
    async def _is_exists_user_by_email(cls, email: str, db: AsyncSession) -> bool:
        query = select(exists().where(CustomUser.email.cast(String) == email))
        try:
            result: bool = await db.scalar(query)
        except IntegrityError as exp:
            logger.error("Ошибка чтения БД при проверке пользователя {}", exp)
            result = True

        return result

    @classmethod
    async def _is_exists_user_by_username_or_email(cls, username: str, email: str, db: AsyncSession) -> bool:
        query = select(exists().where(
            or_(
                CustomUser.username.cast(String) == username,
                CustomUser.email.cast(String) == email
            )
        ))
        try:
            result: bool = await db.scalar(query)
        except IntegrityError as exp:
            logger.error("Ошибка чтения БД при проверке пользователя {}", exp)
            result = True

        return result

    @classmethod
    async def is_unique_user(cls, username: str | None, email: str | None, db: AsyncSession) -> bool:
        """
        Проверка на уникальность для полей username и email. Ищет записи по username и email, если переданы. Вернет
        True, если запись с таким username или email уже существует.
        Args:
            username: str - username
            email: str - email
            db: Session from get_db()
        Returns: True if already exists or False
        """
        if username is not None and email is None:
            result: bool = await cls._is_exists_user_by_username(username=username, db=db)
        elif username is None and email is not None:
            result: bool = await cls._is_exists_user_by_email(email=email, db=db)
        elif username is not None and email is not None:
            result: bool = await cls._is_exists_user_by_username_or_email(username=username, email=email, db=db)
        else:
            raise ValueError("Нужен хотя бы один аргумент: username: str или email: str")

        return result

