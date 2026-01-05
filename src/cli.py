import asyncio

import typer
from rich import print

from src.auth_app.commands.create_superuser import create_superuser


app = typer.Typer()


@app.command()
def createsuperuser(
        username: str = typer.Argument(..., help="Имя пользователя"),
        email: str = typer.Argument(..., help="Электронная почта"),
        pwd: str = typer.Argument(..., help="Пароль")
) -> None:
    msg: str = asyncio.run(create_superuser(username, email, pwd))
    print(f"[bold green]{msg}[/bold green]")
    return


@app.command()
def hello():
    print(f"[bold green]Привет! Это пробное приложение![/bold green]")


if __name__ == '__main__':
    app()
