from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.web.templates import templates

router = APIRouter(tags=["web"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": None},
    )