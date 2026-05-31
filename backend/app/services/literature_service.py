from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.literature import Literature
from app.repositories.literature_repository import LiteratureRepository


class LiteratureService:
    def __init__(self, db: Session) -> None:
        self.repository = LiteratureRepository(db)

    def list_literatures(self) -> list[Literature]:
        return self.repository.list_literatures()

    def get_literature(self, literature_id: int) -> Literature:
        literature = self.repository.get_literature_by_id(literature_id)
        if literature is None:
            raise HTTPException(status_code=404, detail="文献不存在")
        return literature
