from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.database_tutorial import DatabaseTutorial


class DatabaseResource(Base):
    __tablename__ = "database_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(240), nullable=False)
    category_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    use_cases_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    data_types_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    species_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    download_url: Mapped[str | None] = mapped_column(String(500))
    api_url: Mapped[str | None] = mapped_column(String(500))
    region: Mapped[str] = mapped_column(String(120), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tutorials: Mapped[list["DatabaseTutorial"]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
    )
