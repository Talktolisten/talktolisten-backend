from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine
from app.main import app
from app.auth import get_current_user


@pytest.fixture(scope="session")
def db() -> Generator:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def current_user() -> str:
    return "test_user_id"

@pytest.fixture(scope="module")
def client(current_user: str) -> Generator:
    app.dependency_overrides[get_current_user] = lambda: current_user
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_current_user]