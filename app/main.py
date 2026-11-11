from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.session import SessionMiddleware

from app.api.routes import health
from app.core.config import settings
from app.web.routes import admin, agent, auth, client

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="service_desk_session",
    max_age=60*60*24,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def root(request: Request):  # noqa: F821
    user_id = request.session.get("user_id")
    if user_id: 
        
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])