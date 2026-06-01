
def test_create_todo(client, auth_headers):
    response = client.post("/todos", json={"title": "Buy groceries", "description": "Milk and eggs"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["completed"] is False
    assert "id" in data


def test_list_todos(client, auth_headers):
    client.post("/todos", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/todos", json={"title": "Task 2"}, headers=auth_headers)
    response = client.get("/todos", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2


def test_get_todo(client, auth_headers):
    create_resp = client.post("/todos", json={"title": "Get me"}, headers=auth_headers)
    todo_id = create_resp.json()["id"]
    response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == todo_id


def test_update_todo(client, auth_headers):
    create_resp = client.post("/todos", json={"title": "Old title"}, headers=auth_headers)
    todo_id = create_resp.json()["id"]
    response = client.put(f"/todos/{todo_id}", json={"title": "New title", "completed": True}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["completed"] is True


def test_delete_todo(client, auth_headers):
    create_resp = client.post("/todos", json={"title": "Delete me"}, headers=auth_headers)
    todo_id = create_resp.json()["id"]
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 204
    get_resp = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_todos_require_auth(client):
    response = client.get("/todos")
    assert response.status_code == 401