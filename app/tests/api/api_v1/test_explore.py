from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.tests.utils.user import create_random_user
from app.tests.utils.bot import create_random_bot
from app.tests.utils.voice import create_random_voice

def test_get_all_bots(client: TestClient, db: Session) -> None:
    create_random_bot(db)
    response = client.get(f"{settings.API_VERSION}/explore/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_bots_by_category(client: TestClient, db: Session) -> None:
    category = "TV character"
    create_random_bot(db, category=category)
    response = client.get(f"{settings.API_VERSION}/explore/category?category={category}")
    assert response.status_code == 200
    for bot in response.json():
        assert bot["category"] == category

def test_get_bots_by_search(client: TestClient, db: Session) -> None:
    search = "Ammelia"
    create_random_bot(db, bot_name=search)
    response = client.get(f"{settings.API_VERSION}/explore/search?search={search}")
    assert response.status_code == 200
    assert any(search in bot["bot_name"] for bot in response.json())