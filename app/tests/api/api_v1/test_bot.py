from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.tests.utils.user import create_random_user
from app.tests.utils.bot import create_random_bot
from app.tests.utils.voice import create_random_voice


def test_create_bot(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = create_random_voice(db, owner_data.user_id)
    bot_data = {
        "bot_name": "Ammelia",
        "short_description": "Fun bot",
        "description": "This is a fun bot. Always tell you the truth.",
        "profile_picture": "aws.s3.xx",
        "category": "TV character",
        "voice_id": voice_data.voice_id,
        "created_by": owner_data.user_id,
    }
    response = client.post(
        f"{settings.API_VERSION}/bot/",
        json=bot_data,
    )
    content = response.json()
    assert response.status_code == 201
    assert content["bot_name"] == bot_data["bot_name"]
    assert "bot_id" in content, f"'bot_id' is not in response"
    assert content["short_description"] == bot_data["short_description"]
    assert content["description"] == bot_data["description"]
    assert content["profile_picture"] == bot_data["profile_picture"]
    assert content["category"] == bot_data["category"]
    assert content["voice_id"] == bot_data["voice_id"]
    assert content["created_by"] == bot_data["created_by"]


def test_get_bot(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = create_random_voice(db, owner_data.user_id)
    bot_data = {
        "bot_name": "Ammelia",
        "short_description": "Fun bot",
        "description": "This is a fun bot. Always tell you the truth.",
        "profile_picture": "aws.s3.xx",
        "category": "TV character",
        "voice_id": voice_data.voice_id,
        "created_by": owner_data.user_id,
    }
    response = client.post(
        f"{settings.API_VERSION}/bot/",
        json=bot_data,
    )
    content = response.json()
    assert response.status_code == 201
    assert content["bot_name"] == bot_data["bot_name"]
    assert "bot_id" in content, f"'bot_id' is not in response"
    assert content["short_description"] == bot_data["short_description"]
    assert content["description"] == bot_data["description"]
    assert content["profile_picture"] == bot_data["profile_picture"]
    assert content["category"] == bot_data["category"]
    assert content["voice_id"] == bot_data["voice_id"]
    assert content["created_by"] == bot_data["created_by"]

    response = client.get(
        f"{settings.API_VERSION}/bot/{owner_data.user_id}",
    )
    content = response.json()
    assert response.status_code == 200
    assert len(content) == 1
    assert content[0]["bot_name"] == bot_data["bot_name"]
    assert content[0]["short_description"] == bot_data["short_description"]
    assert content[0]["description"] == bot_data["description"]
    assert content[0]["profile_picture"] == bot_data["profile_picture"]
    assert content[0]["category"] == bot_data["category"]
    assert content[0]["voice_id"] == bot_data["voice_id"]
    assert content[0]["created_by"] == bot_data["created_by"]


def test_update_bot(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = create_random_voice(db, owner_data.user_id)
    bot_data = {
        "bot_name": "Ammelia",
        "short_description": "Fun bot",
        "description": "This is a fun bot. Always tell you the truth.",
        "profile_picture": "aws.s3.xx",
        "category": "TV character",
        "voice_id": voice_data.voice_id,
        "created_by": owner_data.user_id,
    }
    response = client.post(
        f"{settings.API_VERSION}/bot/",
        json=bot_data,
    )
    content = response.json()
    assert response.status_code == 201
    assert "bot_id" in content, f"'bot_id' is not in response"
    assert content["bot_name"] == bot_data["bot_name"]
    assert content["short_description"] == bot_data["short_description"]
    assert content["description"] == bot_data["description"]
    assert content["profile_picture"] == bot_data["profile_picture"]
    assert content["category"] == bot_data["category"]
    assert content["voice_id"] == bot_data["voice_id"]
    assert content["created_by"] == bot_data["created_by"]
    bot_update_data = {
        "bot_name": "Ammelia",
        "short_description": "Fun bot",
        "description": "This is a fun bot. Always tell you the truth.",
        "profile_picture": "aws.s3.xx",
        "category": "TV character",
        "voice_id": voice_data.voice_id,
        "created_by": owner_data.user_id,
    }
    response = client.patch(
        f"{settings.API_VERSION}/bot/{content['bot_id']}",
        json=bot_update_data,
    )
    content = response.json()
    assert response.status_code == 200
    assert content["bot_name"] == bot_update_data["bot_name"]
    assert content["short_description"] == bot_update_data["short_description"]
    assert content["description"] == bot_update_data["description"]
    assert content["profile_picture"] == bot_update_data["profile_picture"]
    assert content["category"] == bot_update_data["category"]
    assert content["voice_id"] == bot_update_data["voice_id"]
    assert content["created_by"] == bot_update_data["created_by"]


def test_delete_bot(client: TestClient, db: Session) -> None:
    owner_data = create_random_user(db)
    voice_data = create_random_voice(db, owner_data.user_id)
    bot_data = {
        "bot_name": "Ammelia",
        "short_description": "Fun bot",
        "description": "This is a fun bot. Always tell you the truth.",
        "profile_picture": "aws.s3.xx",
        "category": "TV character",
        "voice_id": voice_data.voice_id,
        "created_by": owner_data.user_id,
    }
    response = client.post(
        f"{settings.API_VERSION}/bot/",
        json=bot_data,
    )
    content = response.json()
    assert response.status_code == 201
    assert "bot_id" in content, f"'bot_id' is not in response"
    assert content["bot_name"] == bot_data["bot_name"]
    assert content["short_description"] == bot_data["short_description"]
    assert content["description"] == bot_data["description"]
    assert content["profile_picture"] == bot_data["profile_picture"]
    assert content["category"] == bot_data["category"]
    assert content["voice_id"] == bot_data["voice_id"]
    assert content["created_by"] == bot_data["created_by"]

    response = client.delete(
        f"{settings.API_VERSION}/bot/{content['bot_id']}",
    )

    assert response.status_code == 204