import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapizero.app import app
from fastapizero.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)  # cria dados

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)  # apaga dados
