from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator


class UserSchema(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=125, description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(max_length=80, description="Электронная почта пользователя")]


class UserRegisterSchema(UserSchema):
    password: Annotated[str, Field(min_length=3, max_length=8, description="Пароль")]


class ChangePasswordSchema(BaseModel):
    old_password: Annotated[str, Field(description="Старый пароль")]
    new_password: Annotated[str, Field(description="Новый пароль")]
    repeat_password: Annotated[str, Field(description="Повтор пароль")]


class UserUpdateSchema(BaseModel):
    username: Annotated[str | None, Field(default=None, description="Пользователь")]
    email: Annotated[EmailStr | None, Field(default=None, description="Электронная почта")]
    first_name: Annotated[str | None, Field(default=None, description="Имя пользователя")]
    second_name: Annotated[str | None, Field(default=None, description="Фамилия пользователя")]
    last_name: Annotated[str | None, Field(default=None, description="Отчество пользователя")]

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, value: str) -> str:
        if value is not None:
            if len(value) == 0:
                raise ValueError("Поле не должно быть пустой строкой. Доступно значение None.")
        return value


class UserWorkSchema(BaseModel):
    id: Annotated[UUID | None, Field(default=None, description="Идентификатор пользователя")]
    username: Annotated[str | None, Field(default=None, description="Пользователь")]
    email: Annotated[EmailStr | None, Field(default=None, description="Электронная почта")]
    first_name: Annotated[str | None, Field(default=None, description="Имя пользователя")]
    second_name: Annotated[str | None, Field(default=None, description="Фамилия пользователя")]
    last_name: Annotated[str | None, Field(default=None, description="Отчество пользователя")]
    is_active: Annotated[bool | None, Field(default=None, description="Активированный пользователь")]
    is_staff: Annotated[bool | None, Field(default=None, description="Сотрудник")]
    is_superuser: Annotated[bool | None, Field(default=None, description="Администратор")]


class UsersAllSchema(BaseModel):
    users: Annotated[list[UserWorkSchema], Field(default_factory=list, description="Пользователи")]
