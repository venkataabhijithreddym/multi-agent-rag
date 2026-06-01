

def test_register(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_username(client, test_user):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "other@example.com",
        "password": "password",
    })
    assert response.status_code == 400


def test_login_success(client, test_user):
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/weather")
    assert response.status_code == 401