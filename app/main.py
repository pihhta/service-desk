from app.core.config import settings

@app.get("/config-check")
def config_check():
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "db_host": settings.database_url.split("@")[-1],  # без пароля
    }