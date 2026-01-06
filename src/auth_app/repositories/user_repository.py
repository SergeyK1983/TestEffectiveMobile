from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import delete, String, update, RowMapping
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.models import CustomUser
from src.auth_app.repositories.base_repository import UserBaseRepo
from src.core.logger import logger

if TYPE_CHECKING:
    from src.auth_app.schemes.user_schemes import UserRegisterSchema, UserWorkSchema


class UserRegisterRepo(UserBaseRepo):
    """ Для регистрации пользователя """

    @classmethod
    async def create_user(cls, user: "UserRegisterSchema", db: AsyncSession) -> RowMapping | None:
        """
        Запись данных нового пользователя в БД.
        Args:
            user: schema UserRegisterSchema
            db: session
        Returns:
            created user's dict fields
        """
        query = (
            insert(
                CustomUser
            ).
            values(
                username=user.username,
                password=user.password,
                email=user.email,
            )
        )
        try:
            await db.execute(query)
            await db.commit()

            result = await db.execute(
                cls._select_user_fields().where(CustomUser.username.cast(String) == user.username)
            )
            user_created: RowMapping = result.mappings().first()
        except IntegrityError as exp:
            logger.error("Ошибка записи в БД при создании пользователя: {err}", err=exp)
            return

        logger.success("Пользователь {name} зарегистрирован, email {email}", name=user.username, email=user.email)
        return user_created


class UserRegisteredRepo(UserBaseRepo):
    """ Для зарегистрированных пользователей """

    @classmethod
    async def delete_user(cls, user: "UserWorkSchema", db: AsyncSession) -> RowMapping | None:
        """
        Удаление записи данных пользователя из БД
        Args:
            user: UserSchema data
            db: Session from get_db()
        """
        query = (
            delete(
                CustomUser
            ).
            where(
                CustomUser.username.cast(String) == user.username,
                CustomUser.email.cast(String) == user.email,
            ).
            returning(
                CustomUser.username,
                CustomUser.email,
            )
        )
        try:
            result = await db.execute(query)
            await db.commit()
        except IntegrityError as exp:
            logger.error("Ошибка удаления данных пользователя из БД {}", exp)
            return

        fields = result.mappings().first()
        logger.success("Пользователь {} удалён, email {}", user.username, user.email)
        return fields

    @classmethod
    async def update_one_user_by_id(cls, user_id: UUID, data: dict, db: AsyncSession) -> RowMapping | None:
        """
        Изменение данных записи о пользователе в БД.
        Args:
            user_id: user id
            data: data for update
            db: Session from get_db()

        Returns: RowMapping user data
        """
        query = (
            update(
                CustomUser
            ).
            where(
                CustomUser.id == user_id
            ).
            returning(
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
        )

        try:
            result = await db.execute(query, data)
            await db.commit()
        except IntegrityError as exp:
            logger.error("Ошибка изменения данных пользователя из БД {}", exp)
            return

        user_map: RowMapping = result.mappings().first()
        logger.success("Данные пользователя id - {} изменены", user_id)
        return user_map

    @classmethod
    async def read_one_user_by_id(cls, user_id: UUID, db: AsyncSession) -> RowMapping | None:
        query = cls._select_user_fields().where(CustomUser.id == user_id)

        result = await cls._select_execute_query(query, db)
        if result is None:
            return None
        user_map: RowMapping = result.mappings().first()
        return user_map

    @classmethod
    async def read_one_user_by_username(cls, username: str, db: AsyncSession) -> RowMapping | None:
        query = cls._select_user_fields().where(CustomUser.username.cast(String) == username)

        result = await cls._select_execute_query(query, db)
        if result is None:
            return None
        user_map: RowMapping = result.mappings().first()
        return user_map

    @classmethod
    async def read_one_user_by_email(cls, email: str, db: AsyncSession) -> RowMapping | None:
        query = cls._select_user_fields().where(CustomUser.email.cast(String) == email)

        result = await cls._select_execute_query(query, db)
        if result is None:
            return None
        user_map: RowMapping = result.mappings().first()
        return user_map
