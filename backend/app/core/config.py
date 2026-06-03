from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bioinformatics Cloud Platform API"
    api_v1_prefix: str = "/api"
    database_url: str = (
        "postgresql+psycopg2://bioinfo:bioinfo_password@localhost:5432/bioinfo"
    )

    @property
    def resolved_database_url(self) -> str:
        """Render 提供的是 postgres://，SQLAlchemy 需要 postgresql://"""
        db = self.database_url
        if db.startswith("postgres://"):
            db = "postgresql+psycopg2://" + db[len("postgres://"):]
        elif db.startswith("postgresql://"):
            db = "postgresql+psycopg2://" + db[len("postgresql://"):]
        return db

    cors_origins: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

