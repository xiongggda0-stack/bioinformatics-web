from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.literature import Literature


class LiteratureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_literatures(self) -> list[Literature]:
        statement = select(Literature).order_by(
            Literature.publication_year.desc(), Literature.id.desc()
        )
        return list(self.db.scalars(statement).all())

    def get_literature_by_id(self, literature_id: int) -> Literature | None:
        return self.db.get(Literature, literature_id)
