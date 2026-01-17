from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="src/templates")

router = APIRouter(tags=["homepage"])


@router.get("/", name="home")
async def homepage(request: Request):
    return templates.TemplateResponse(request, "index.html", status_code=status.HTTP_200_OK)
