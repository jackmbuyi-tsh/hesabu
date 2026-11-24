import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mmgateway.api.main import app
from mmgateway.db import Base, get_session

# Tests run on SQLite in memory by default. Set MMG_TEST_DATABASE_URL to an
# empty PostgreSQL database to run them there instead.
TEST_DATABASE_URL = os.environ.get("MMG_TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")


@pytest.fixture
def engine():
    kwargs = {}
    if TEST_DATABASE_URL.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    engine = create_engine(TEST_DATABASE_URL, **kwargs)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
    def override():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
