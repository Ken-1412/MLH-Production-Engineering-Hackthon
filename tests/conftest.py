import pytest
import os

os.environ["DATABASE_NAME"]     = "hackathon_test"
os.environ["DATABASE_HOST"]     = "127.0.0.1"
os.environ["DATABASE_PORT"]     = "5432"
os.environ["DATABASE_USER"]     = "postgres"
os.environ["DATABASE_PASSWORD"] = "postgres"

from app import create_app
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.event import Event

MODELS = [Event, Url, User]  # children first for drop order

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
        username="fixture_u_zx9",
        email="fixture_zx9@test.com"
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
