from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    MONGO_URI: str = "mongodb+srv://heirloom_user:heirloom123@cluster0.2yihed4.mongodb.net/?retryWrites=true&w=majority"
    DB_NAME: str = "heirloom_db"
    SECRET_KEY: str = "super_secret_hackathon_key_12345"
    WEB3_PROVIDER_URI: str = "http://127.0.0.1:8545"

settings = Settings()