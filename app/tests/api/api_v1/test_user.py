from app.config import settings
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.utils import format_dob_str


def test_create_user(client: TestClient, db: Session) -> None:
    username = random_lower_string()
    gmail = random_email()
    first_name = random_lower_string()
    last_name = random_lower_string()
    profile_picture = random_lower_string()
    user = {
        "user_id": random_lower_string(),
        "dob": "12 / 12 / 1999",
        "username": username,
        "gmail": gmail,
        "first_name": first_name,
        "last_name": last_name,
        "profile_picture": profile_picture,
    }

    response = client.post(f"{settings.API_VERSION}/user/signup", json=user)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user["username"]
    assert data["gmail"] == user["gmail"]
    assert data["first_name"] == user["first_name"]
    assert data["last_name"] == user["last_name"]
    assert data["profile_picture"] == user["profile_picture"]
    assert data["dob"] == user["dob"]
    assert data["subscription"] == "standard"
    assert data["bio"] == None
    assert data["status"] == "inactive"
    assert data["theme"] == "light"


def test_get_user(client: TestClient, db: Session) -> None:

    username = random_lower_string()
    gmail = random_email()
    first_name = random_lower_string()
    last_name = random_lower_string()
    profile_picture = random_lower_string()
    user = {
        "user_id": random_lower_string(),
        "dob": "12 / 12 / 1999",
        "username": username,
        "gmail": gmail,
        "first_name": first_name,
        "last_name": last_name,
        "profile_picture": profile_picture,
    }

    response = client.post(f"{settings.API_VERSION}/user/signup", json=user)
    data = response.json()

    response = client.get(f"{settings.API_VERSION}/user/{data['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user["username"]
    assert data["gmail"] == user["gmail"]
    assert data["first_name"] == user["first_name"]
    assert data["last_name"] == user["last_name"]
    assert data["profile_picture"] == user["profile_picture"]
    assert data["dob"] == user["dob"]
    assert data["subscription"] == "standard"
    assert data["bio"] == None
    assert data["status"] == "inactive"
    assert data["theme"] == "light"


def test_update_user(client: TestClient, db: Session) -> None:
    username = random_lower_string()
    gmail = random_email()
    first_name = random_lower_string()
    last_name = random_lower_string()
    profile_picture = random_lower_string()
    user = {
        "user_id": random_lower_string(),
        "dob": "12 / 12 / 1999",
        "username": username,
        "gmail": gmail,
        "first_name": first_name,
        "last_name": last_name,
        "profile_picture": profile_picture,
    }

    response = client.post(f"{settings.API_VERSION}/user/signup", json=user)
    data = response.json()

    user_update = {
        "username": random_lower_string(),
        "gmail": random_email(),
        "first_name": random_lower_string(),
        "last_name": random_lower_string(),
        "profile_picture": random_lower_string(),
        "dob": "12 / 12 / 1999",
    }
    response = client.patch(
        f"{settings.API_VERSION}/user/{data['user_id']}", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_update["username"]
    assert data["gmail"] == user_update["gmail"]
    assert data["first_name"] == user_update["first_name"]
    assert data["last_name"] == user_update["last_name"]
    assert data["profile_picture"] == user_update["profile_picture"]
    assert data["dob"] == user_update["dob"]
    assert data["subscription"] == "standard"
    assert data["bio"] == None
    assert data["status"] == "inactive"
    assert data["theme"] == "light"
