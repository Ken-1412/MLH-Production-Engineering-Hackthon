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
from app.models.url import Url
from app.models.user import User
from app.models.event import Event  # noqa: E402


@pytest.fixture(scope="function")
def app():
    application = create_app()
    application.config["TESTING"] = True
    with application.app_context():
        db.create_tables([Url, User, Event], safe=True)
        yield application
        db.drop_tables([Url, User, Event], safe=True)


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def sample(app):
    """One valid record for use in GET/PUT/DELETE tests."""
    return Url.create(
        user_id=1,
        short_code="TEST01",
        original_url="https://example.com/test",
        title="Test URL",
        is_active=True,
    )
