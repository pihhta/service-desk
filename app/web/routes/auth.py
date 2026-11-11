from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import authenticate_user
from app.db.session import get_db
from app.web.templates import templates

router = APIRouter(tags=["web"])

ROLE_HOME = {
    "admin":"/admin",
    "manager":"/manager",
    "agent":"/agent",
    "client":"/client",
}

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": None},
    )

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "user": None,
                "error": "Неверный email или пароль",
            },
            status_code=401,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(
        url=ROLE_HOME.get(user.role, "/login"),
        status_code=303
    )