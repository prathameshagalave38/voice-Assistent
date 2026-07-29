from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    mongodb_uri: str = Field(..., env="MONGODB_URI")
    database_name: str = Field("vapi_conversations", env="DATABASE_NAME")
    api_key: str = Field(..., env="API_KEY")
    port: int = Field(8000, env="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
