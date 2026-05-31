from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Literature(Base):
    __tablename__ = "literatures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    authors: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    journal: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    doi: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    abstract_text: Mapped[str] = mapped_column(Text, nullable=False)
    pipeline_id: Mapped[int | None] = mapped_column(
        ForeignKey("pipelines.id"), nullable=True, index=True
    )
    algorithm_id: Mapped[int | None] = mapped_column(
        ForeignKey("algorithms.id"), nullable=True, index=True
    )
