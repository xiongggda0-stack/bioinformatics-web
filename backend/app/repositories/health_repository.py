from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ping_database(self) -> bool:
        self.db.execute(text("SELECT 1"))
        return True

