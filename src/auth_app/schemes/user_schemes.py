from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, AfterValidator

from src.auth_app.schemes.validators import validate_password, validate_username

ValidPassword = Annotated[str, AfterValidator(validate_password)]
ValidUsername = Annotated[str, AfterValidator(validate_username)]


class UserSchema(BaseModel):
    username: Annotated[ValidUsername, Field(min_length=4, max_length=125, description="Имя пользователя в системе")]
    email: Annotated[EmailStr, Field(max_length=80, description="Электронная почта пользователя")]


class UserRegisterSchema(UserSchema):
    password: Annotated[ValidPassword, Field(description="Пароль")]


class ChangePasswordSchema(BaseModel):
    old_password: Annotated[str, Field(description="Старый пароль")]
    new_password: Annotated[ValidPassword, Field(description="Новый пароль")]
    repeat_password: Annotated[str, Field(description="Повтор пароль")]


class UserUpdateSchema(BaseModel):
    username: Annotated[
        ValidUsername | None,
        Field(default=None, min_length=4, max_length=125, description="Пользователь")
    ]
    email: Annotated[EmailStr | None, Field(default=None, description="Электронная почта")]
    first_name: Annotated[str | None, Field(default=None, description="Имя пользователя")]
    second_name: Annotated[str | None, Field(default=None, description="Фамилия пользователя")]
    last_name: Annotated[str | None, Field(default=None, description="Отчество пользователя")]


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


class UserServiceFieldsSchema(BaseModel):
    username: Annotated[str, Field(exclude=True, description="Пользователь")]
    is_active: Annotated[bool | None, Field(default=None, description="Активированный пользователь")]
    is_staff: Annotated[bool | None, Field(default=None, description="Сотрудник")]
    is_superuser: Annotated[bool | None, Field(default=None, description="Администратор")]
