from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Memex Backend"
    debug: bool = False
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
