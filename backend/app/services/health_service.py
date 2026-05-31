from sqlalchemy.orm import Session

from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, db: Session) -> None:
        self.repository = HealthRepository(db)

    def check(self) -> dict[str, str]:
        database_ok = self.repository.ping_database()
        return {
            "service": "ok",
            "database": "ok" if database_ok else "error",
        }

