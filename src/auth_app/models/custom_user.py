import uuid
from datetime import datetime

from sqlalchemy import String, UUID, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CustomUser(Base):
    """
    Пользователь.
    """
    __tablename__ = "custom_users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания"
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Дата изменения"
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True, comment="Пользователь"
    )
    password: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Имя"
    )
    second_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Фамилия"
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Отчество"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Суперпользователь"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="Активен"
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Персонал"
    )

    __table_args__ = (
        UniqueConstraint("username", name="user_username_key_uniq"),
        UniqueConstraint("email", name="user_email_key_uniq"),
    )

    def __repr__(self):
        return f"{self.id}-{self.username}"
