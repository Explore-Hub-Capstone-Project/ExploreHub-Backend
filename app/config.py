from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_NAME: str = "ExploreHub-DB"
    PORT: int = 5001
    MONGODB_URI: str = "mongodb://localhost:5000"
    SECRET_KEY: str = Field(None, env="SECRET_KEY")
    X_RAPIDAPI_KEY: str = Field(None, env="X-RAPIDAPI-KEY")
    X_RAPIDAPI_HOST: str = Field(None, env="X_RAPIDAPI_HOST")
    WEATHER_API_KEY: str = Field(None, env="WEATHER_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
