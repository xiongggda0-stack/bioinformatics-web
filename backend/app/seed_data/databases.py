import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource


SEED_PATH = Path(__file__).with_name("database_resources.json")


def load_database_resources() -> list[dict[str, Any]]:
    with SEED_PATH.open(encoding="utf-8") as seed_file:
        return json.load(seed_file)


def seed_databases(db: Session) -> None:
    existing_slugs = set(db.scalars(select(DatabaseResource.slug)).all())

    for item in load_database_resources():
        if item["slug"] in existing_slugs:
            continue

        db.add(DatabaseResource(**item))
        existing_slugs.add(item["slug"])

    db.commit()
