import os

import pytest

# Use a separate test database — never pollute the dev DB
os.environ["DATABASE_NAME"] = "hackathon_test"
os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_PORT"] = "5432"
os.environ["DATABASE_USER"] = "postgres"
os.environ["DATABASE_PASSWORD"] = "postgres"

from app import create_app  # noqa: E402
from app.database import db  # noqa: E402
from app.models.url import Url  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.event import Event  # noqa: E402

MODELS = [Event, Url, User]  # drop order: children before parents


@pytest.fixture(scope="function")
def app():
    application = create_app()
    application.config["TESTING"] = True
    with application.app_context():
        db.create_tables(MODELS, safe=True)
        yield application
        db.drop_tables(MODELS, safe=True)


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def sample_user(app):
    return User.create(
        username="fixture_user_x7k",
        email="fixture_x7k@test.com"
    )


@pytest.fixture(scope="function")
def sample(app):
    """One valid Url record for use in GET/PUT/DELETE tests."""
    return Url.create(
        user_id=1,
        short_code="TEST01",
        original_url="https://example.com/test",
        title="Test URL",
        is_active=True,
    )


@pytest.fixture(scope="function")
def sample_url(app, sample_user):
    return Url.create(
        user_id=sample_user.id,
        short_code="fixturecd1",
        original_url="https://example.com",
        title="Fixture URL",
        is_active=True
    )


@pytest.fixture(scope="function")
def inactive_url(app, sample_user):
    return Url.create(
        user_id=sample_user.id,
        short_code="inactivex1",
        original_url="https://example.com",
        title="Inactive URL",
        is_active=False
    )
