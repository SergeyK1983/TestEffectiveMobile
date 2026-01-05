from sqlalchemy import String, RowMapping
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_app.models import CustomUser
from src.auth_app.repositories.base_repository import UserBaseRepo
from src.core.logger import logger


class SuperuserRepo(UserBaseRepo):

    @classmethod
    async def create_superuser(cls, username: str, email: str, password: str, db: AsyncSession) -> bool:
        """
        Создание суперпользователя
        Args:
            username: username
            email: email
            password: password
            db: session
        Returns:
            True if created, else False
        """
        query = (
            insert(
                CustomUser
            ).
            values(
                username=username,
                password=password,
                email=email,
                is_superuser=True,
                is_staff=True,
                is_active=True,
            )
        )
        try:
            await db.execute(query)
            await db.commit()

            result = await db.execute(
                cls._select_user_fields().where(CustomUser.username.cast(String) == username)
            )
            user_created: RowMapping = result.mappings().first()
        except IntegrityError as exp:
            logger.error("Ошибка записи в БД при создании суперпользователя: {err}", err=exp)
            return False
        if user_created is None:
            return False

        logger.success("Администратор {name} создан, email {email}", name=username, email=email)
        return True
