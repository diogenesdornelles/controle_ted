from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )
    gmail_pwd: str = ""
    user_pwd: str = ""
    user_app: str = ""


settings = Settings()

if __name__ == "__main__":
    s = Settings()
    print(s.model_dump())
