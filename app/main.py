from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import health
from app.core.config import settings
from app.web.routes import admin, agent, auth, client

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])