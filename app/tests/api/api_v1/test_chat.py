from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.tests.utils.user import create_random_user
from app.tests.utils.bot import create_random_bot
from app.tests.utils.voice import create_random_voice

def test_create_chat(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )

    assert response.status_code == 201


def test_get_chat(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"{settings.API_VERSION}/chat/{user.user_id}",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == user.user_id
    assert response.json()[0]["bot_id1"] == bot.bot_id
    assert response.json()[0]["bot_id2"] == None
    assert response.json()[0]["bot_id3"] == None
    assert response.json()[0]["bot_id4"] == None
    assert response.json()[0]["bot_id5"] == None


def test_delete_chat(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "chat_id" in content, f"'chat_id' is not in response"

    response = client.delete(
        f"{settings.API_VERSION}/chat/{content['chat_id']}",
    )

    assert response.status_code == 204


def test_create_message_by_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "chat_id" in content, f"'chat_id' is not in response"

    response = client.post(
        f"{settings.API_VERSION}/chat/{content['chat_id']}/message",
        json={
            "message": "Hello, this is a test message.",
            "created_by_user": user.user_id,
            "is_bot": False,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "message_id" in content, f"'message_id' is not in response"
    assert content["is_bot"] == False, f"'is_bot' is not False"


def test_get_messages_by_chat(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "chat_id" in content, f"'chat_id' is not in response"

    response = client.post(
        f"{settings.API_VERSION}/chat/{content['chat_id']}/message",
        json={
            "message": "Hello, this is a test message.",
            "created_by_user": user.user_id,
            "is_bot": False,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "message_id" in content, f"'message_id' is not in response"
    assert content["is_bot"] == False, f"'is_bot' is not False"

    response = client.get(
        f"{settings.API_VERSION}/chat/{content['chat_id']}/message",
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["message"] == "Hello, this is a test message."
    assert response.json()[0]["created_by_user"] == user.user_id
    assert response.json()[0]["is_bot"] == False
    assert "user_id" in response.json()[0], f"'user_id' is not in response"
    assert "bot_id" in response.json()[0], f"'bot_id' is not in response"


def test_delete_message_by_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    bot = create_random_bot(db, user.user_id)

    response = client.post(
        f"{settings.API_VERSION}/chat/",
        json={
            "user_id": user.user_id,
            "bot_id1": bot.bot_id,
            "bot_id2": None,
            "bot_id3": None,
            "bot_id4": None,
            "bot_id5": None,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "chat_id" in content, f"'chat_id' is not in response"

    response = client.post(
        f"{settings.API_VERSION}/chat/{content['chat_id']}/message",
        json={
            "message": "Hello, this is a test message.",
            "created_by_user": user.user_id,
            "is_bot": False,
        },
    )
    content = response.json()
    assert response.status_code == 201
    assert "message_id" in content, f"'message_id' is not in response"
    assert content["is_bot"] == False, f"'is_bot' is not False"

    response = client.delete(
        f"{settings.API_VERSION}/chat/{content['chat_id']}/{content['message_id']}",
    )
    assert response.status_code == 204