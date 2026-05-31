from sqlalchemy import text

from app.core.database import Base, SessionLocal, engine
from app.seed_data import (
    seed_algorithms,
    seed_databases,
    seed_database_tutorials,
    seed_literatures,
    seed_pipelines,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.execute(
            text(
                "ALTER TABLE pipelines "
                "ADD COLUMN IF NOT EXISTS metadata_json JSON NOT NULL DEFAULT '{}'"
            )
        )
        db.execute(
            text(
                "ALTER TABLE pipelines "
                "ADD COLUMN IF NOT EXISTS category_key VARCHAR(80) NOT NULL DEFAULT 'other'"
            )
        )
        db.execute(
            text(
                "ALTER TABLE pipelines "
                "ADD COLUMN IF NOT EXISTS category_name VARCHAR(120) NOT NULL DEFAULT '其他分析流程'"
            )
        )
        db.execute(
            text(
                "ALTER TABLE algorithms "
                "ADD COLUMN IF NOT EXISTS category_key VARCHAR(80) NOT NULL DEFAULT 'other'"
            )
        )
        db.execute(
            text(
                "ALTER TABLE algorithms "
                "ADD COLUMN IF NOT EXISTS category_name VARCHAR(120) NOT NULL DEFAULT '其他算法工具'"
            )
        )
        db.execute(
            text(
                "ALTER TABLE algorithms "
                "ADD COLUMN IF NOT EXISTS tool_type VARCHAR(80) NOT NULL DEFAULT '命令行软件'"
            )
        )
        db.commit()
        seed_pipelines(db)
        seed_algorithms(db)
        seed_literatures(db)
        seed_databases(db)
        seed_database_tutorials(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print(
        "Database initialized with pipeline, algorithm, literature, "
        "database and tutorial data."
    )
