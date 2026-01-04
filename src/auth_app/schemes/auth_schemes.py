from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class AuthSchema(BaseModel):
    """ Login """

    username: Annotated[str | None, Field(default=None, description="Имя пользователя")]
    email: Annotated[str | None, Field(default=None, description="Почта пользователя")]
    password: Annotated[str, Field(description="Пароль")]

    @model_validator(mode="after")
    def required_one(self):
        if not self.username and not self.email:
            raise ValueError("Имя пользователя или почта должны быть введены")
        return self
