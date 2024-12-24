import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapizero.app import app
from fastapizero.database import get_session
from fastapizero.models import User, table_registry


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)  # cria dados

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)  # apaga dados


@pytest.fixture
def user(session):
    user = User(
        username='user_test',
        email='email@test.com',
        password='password',
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
