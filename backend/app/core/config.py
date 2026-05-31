from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bioinformatics Cloud Platform API"
    api_v1_prefix: str = "/api"
    database_url: str = (
        "postgresql+psycopg2://bioinfo:bioinfo_password@localhost:5432/bioinfo"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

