class Settings(BaseSettings):
    app_name: str = "Service Desk"
    debug: bool = False
    database_url: str          # обязательное
    secret_key: str            # обязательное
    access_token_expire_minutes: int = 60
    