from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_name: str = "ExploreHub-DB"
    port: int = "5000"
    MONGODB_URI: str = "mongodb://localhost:5000"
    SECRET_KEY: str
    X_RAPIDAPI_KEY: str
    X_RAPIDAPI_HOST: str
    WEATHER_API_KEY: str = Field(None, env="WEATHER_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
