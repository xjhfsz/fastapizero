from contextlib import contextmanager
from datetime import datetime

import pytest
from factory import (
    Factory,
    Faker,
    LazyAttribute,
    Sequence,
    fuzzy,
)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fastapizero.app import app
from fastapizero.database import get_session
from fastapizero.models import (
    Todo,
    TodoState,
    User,
    table_registry,
)
from fastapizero.security import get_password_hash


class UserFactory(Factory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'test{n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = LazyAttribute(lambda obj: f'senha_{obj.username}')


class TodoFactory(Factory):
    class Meta:
        model = Todo

    title = Faker('text')
    description = Faker('text')
    state = fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture(scope='function')
def session(engine):
    table_registry.metadata.create_all(engine)  # cria dados

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)  # apaga dados


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    password = 'password'

    user = UserFactory(
        password=get_password_hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']
