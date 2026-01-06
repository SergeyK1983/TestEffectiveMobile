from uuid import UUID

from sqlalchemy import select, String, update, Select, RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.models import CustomUser
from src.auth_app.repositories.base_repository import UserBaseRepo
from src.core.logger import logger


class UserPasswordRepo(UserBaseRepo):

    @classmethod
    async def read_user_with_password(
            cls, username: str | None, email: str | None, db: AsyncSession
    ) -> CustomUser | None:

        if username:
            query = cls._get_query_by_username(username)
        else:
            query = cls._get_query_by_email(email)

        result = await cls._select_execute_query(query, db)
        if result is None:
            return None

        user_instance = result.scalar_one_or_none()
        return user_instance

    @staticmethod
    def _get_query_by_username(username: str) -> Select:
        query = select(CustomUser).where(CustomUser.username.cast(String) == username)
        return query

    @staticmethod
    def _get_query_by_email(email: str) -> Select:
        query = select(CustomUser).where(CustomUser.email.cast(String) == email)
        return query

    @classmethod
    async def update_user_password(cls, user_id: UUID, password: str, db: AsyncSession) -> RowMapping | None:
        """
        Обновляет запись пользователя в БД - смена пароля.
        Args:
            user_id: id of a user
            password: new password to update user
            db: Session from get_db()
        """
        query = (
            update(
                CustomUser
            ).
            where(
                CustomUser.id == user_id
            ).
            values(
                password=password,
            ).
            returning(
                CustomUser.id,
                CustomUser.username
            )
        )
        try:
            result = await db.execute(query)
            await db.commit()
        except IntegrityError as exp:
            logger.error("Ошибка изменения записи в БД при смене пароля пользователя: {err}", err=exp)
            return

        fields = result.mappings().first()

        logger.success("Обновлен пароль пользователя {}", fields.get("username"))
        return fields

