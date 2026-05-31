from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.database_resource import DatabaseResource


class DatabaseTutorial(Base):
    __tablename__ = "database_tutorials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    database_resource_id: Mapped[int] = mapped_column(
        ForeignKey("database_resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    steps_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    example_query: Mapped[str | None] = mapped_column(Text)
    entry_url: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    resource: Mapped["DatabaseResource"] = relationship(back_populates="tutorials")
