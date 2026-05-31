import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial


SEED_PATH = Path(__file__).with_name("database_tutorials.json")


def load_database_tutorials() -> list[dict[str, Any]]:
    with SEED_PATH.open(encoding="utf-8") as seed_file:
        return json.load(seed_file)


def seed_database_tutorials(db: Session) -> None:
    existing_slugs = set(db.scalars(select(DatabaseTutorial.slug)).all())
    resources_by_slug = {
        resource.slug: resource
        for resource in db.scalars(select(DatabaseResource)).all()
    }

    for item in load_database_tutorials():
        if item["slug"] in existing_slugs:
            continue

        resource_slug = item["resource_slug"]
        resource = resources_by_slug.get(resource_slug)
        if resource is None:
            raise ValueError(f"Database resource does not exist: {resource_slug}")

        tutorial_data = {
            key: value for key, value in item.items() if key != "resource_slug"
        }
        db.add(DatabaseTutorial(resource=resource, **tutorial_data))
        existing_slugs.add(item["slug"])

    db.commit()
