from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine
from app.main import app


@pytest.fixture(scope="session")
def db() -> Generator:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c