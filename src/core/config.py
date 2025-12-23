from pathlib import Path

from cryptography.hazmat.primitives import serialization
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings, case_sensitive=True):

    # database
    DB_NAME: str = Field(alias="DB_NAME")
    DB_USER: str = Field(alias="DB_USER")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: str = Field(alias="DB_PORT")
    ECHO: bool = Field(alias="ECHO")

    # auth
    PASSWORD: str = Field(alias="PASSWORD")
    ALGORITHM: str = Field(alias="ALGORITHM")
    PRIVATE_KEY: str = Field(alias="PRIVATE_KEY")
    PUBLIC_KEY: str = Field(alias="PUBLIC_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_HOURS: int = Field(alias="REFRESH_TOKEN_EXPIRE_HOURS")

    # App
    APPLICATION: str = Field(alias="APPLICATION")
    LEVEL_LOG: str = Field(alias="LEVEL_LOG")
    RELOAD: bool = Field(alias="RELOAD")
    PORT: int = Field(alias="PORT")

    # Redis
    REDIS_HOST: str = Field(alias="REDIS_HOST")
    REDIS_PORT: int = Field(alias="REDIS_PORT")
    REDIS_PASS_FILE: str = Field(alias="REDIS_PASS_FILE")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def postgresql_url(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def async_postgresql_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def public_key(self):
        with open(BASE_DIR / self.PUBLIC_KEY, "rb") as f:
            key = f.read()
        return key

    @property
    def private_key(self):
        with open(BASE_DIR / self.PRIVATE_KEY, "rb") as f:
            key = f.read()

        with open(BASE_DIR / self.PASSWORD, "rb") as f:
            password = f.read()

        private_key = serialization.load_pem_private_key(
            key,
            password=password
        )
        return private_key

    @property
    def redis_pass(self) -> str:
        with open(BASE_DIR / self.REDIS_PASS_FILE, "r") as f:
            password = f.read()
        return password


settings = Settings()
