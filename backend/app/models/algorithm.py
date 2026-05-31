from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Algorithm(Base):
    __tablename__ = "algorithms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category_key: Mapped[str] = mapped_column(
        String(80), nullable=False, index=True, default="other"
    )
    category_name: Mapped[str] = mapped_column(
        String(120), nullable=False, default="其他算法工具"
    )
    tool_type: Mapped[str] = mapped_column(
        String(80), nullable=False, index=True, default="命令行软件"
    )
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    # Benchmark data consumed by the frontend ECharts component.
    performance_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    markdown_docs: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
