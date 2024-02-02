from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.config import settings

from app.tests.utils.user import create_random_user
from app.tests.utils.voice import create_random_voice

def test_create_voice_by_user(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = {
        "voice_name": "Ammelia",
        "voice_description": "Funny voice",
        "created_by": owner_data.user_id,
    }

    response = client.post(f"{settings.API_VERSION}/voice/",json=voice_data)
    assert response.status_code == 201
    content = response.json()
    assert content["voice_name"] == voice_data["voice_name"]
    assert content["voice_description"] == voice_data["voice_description"]
    assert "voice_id" in content, f"'voice_id' is not in response"

def test_get_voice_by_user(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = {
        "voice_name": "Ammelia",
        "voice_description": "Funny voice",
        "created_by": owner_data.user_id,
    }

    response = client.post(f"{settings.API_VERSION}/voice/",json=voice_data)
    assert response.status_code == 201

    response = client.get(f"{settings.API_VERSION}/voice/user/{owner_data.user_id}",) #voice_id
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
    assert content[0]["voice_name"] == voice_data["voice_name"]
    assert content[0]["voice_description"] == voice_data["voice_description"]
    assert "voice_id" in content[0], f"'voice_id' is not in response"

def test_get_voice_all(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = {
        "voice_name": "Ammelia",
        "voice_description": "Funny voice",
        "created_by": owner_data.user_id,
    }

    response = client.post(f"{settings.API_VERSION}/voice/",json=voice_data)
    assert response.status_code == 201

    response = client.get(f"{settings.API_VERSION}/voice/{id}") #voice_id
    assert response.status_code == 200
    content = response.json()
    assert content["voice_name"] == voice_data["voice_name"]
    assert content["voice_description"] == voice_data["voice_description"]
    assert "voice_id" in content, f"'voice_id' is not in response"

def test_update_voice(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = {
        "voice_name": "Ammelia",
        "voice_description": "Funny voice",
        "created_by": owner_data.user_id,
    }

    response = client.post(f"{settings.API_VERSION}/voice/",json=voice_data)
    assert response.status_code == 201
    content = response.json()

    voice_update_data = {
        "voice_name": "Updated Name",
        "voice_description": "Updated description",
        "created_by": owner_data.user_id,
    }
    response = client.patch(
        f"{settings.API_VERSION}/voice/{content['voice_id']}",
        json=voice_update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["voice_name"] == voice_update_data["voice_name"]
    assert content["voice_description"] == voice_update_data["voice_description"]
    assert "voice_id" in content, f"'voice_id' is not in response"

def test_delete_voice(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = {
        "voice_name": "Ammelia",
        "voice_description": "Funny voice",
        "created_by": owner_data.user_id,
    }
    response = client.post(
        f"{settings.API_VERSION}/voice/",
        json=voice_data,
    )
    assert response.status_code == 201
    content = response.json()

    response = client.delete(
        f"{settings.API_VERSION}/voice/{content['voice_id']}",
    )
    assert response.status_code == 204