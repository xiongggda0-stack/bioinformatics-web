from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bioinformatics Cloud Platform API"
    api_v1_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000"
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    database_url: str = (
        "postgresql+psycopg2://bioinfo:bioinfo_password@localhost:5432/bioinfo"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()

