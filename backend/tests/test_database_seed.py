from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.database_resource import DatabaseResource
from app.models.database_tutorial import DatabaseTutorial
from app.seed_data.databases import seed_databases
from app.seed_data.database_tutorials import seed_database_tutorials


def test_database_seed_is_idempotent(db_session: Session) -> None:
    seed_databases(db_session)
    seed_database_tutorials(db_session)

    first_resource_count = db_session.scalar(select(func.count(DatabaseResource.id)))
    first_tutorial_count = db_session.scalar(select(func.count(DatabaseTutorial.id)))

    seed_databases(db_session)
    seed_database_tutorials(db_session)

    second_resource_count = db_session.scalar(select(func.count(DatabaseResource.id)))
    second_tutorial_count = db_session.scalar(select(func.count(DatabaseTutorial.id)))

    assert first_resource_count is not None
    assert first_resource_count >= 40
    assert first_tutorial_count is not None
    assert first_tutorial_count >= 3
    assert second_resource_count == first_resource_count
    assert second_tutorial_count == first_tutorial_count


def test_tutorial_seed_links_each_tutorial_to_a_resource(
    db_session: Session,
) -> None:
    seed_databases(db_session)
    seed_database_tutorials(db_session)

    tutorials = list(db_session.scalars(select(DatabaseTutorial)).all())

    assert tutorials
    assert all(tutorial.resource is not None for tutorial in tutorials)
    assert len({tutorial.slug for tutorial in tutorials}) == len(tutorials)
