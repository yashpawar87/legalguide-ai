from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    OPENROUTER_API_KEY: str
    DATABASE_URL: str
    FIREBASE_CREDENTIALS_PATH: str
    FIREBASE_WEB_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_ENDPOINT: str
    LANGCHAIN_PROJECT: str
    FRONTEND_URL: str = "http://localhost:8501"
    MAX_FILE_SIZE_MB: int = 20
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
