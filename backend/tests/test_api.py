from datetime import date


def register_user(client, email: str, password: str, role: str):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password, "role": role},
    )


def login_token(client, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_and_login(client):
    register = register_user(client, "admin@test.com", "password123", "admin")
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": "admin@test.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    payload = login.json()
    assert payload["token_type"] == "bearer"
    assert payload["role"] == "admin"


def test_records_permissions(client):
    register_user(client, "admin@test.com", "password123", "admin")
    register_user(client, "analyst@test.com", "password123", "analyst")
    register_user(client, "viewer@test.com", "password123", "viewer")

    admin_token = login_token(client, "admin@test.com", "password123")
    analyst_token = login_token(client, "analyst@test.com", "password123")
    viewer_token = login_token(client, "viewer@test.com", "password123")

    create_payload = {
        "amount": 5000,
        "type": "income",
        "category": "Consulting",
        "date": date(2026, 4, 1).isoformat(),
        "notes": "Invoice paid",
    }

    create_by_admin = client.post(
        "/records",
        json=create_payload,
        headers=auth_header(admin_token),
    )
    assert create_by_admin.status_code == 201

    create_by_analyst = client.post(
        "/records",
        json=create_payload,
        headers=auth_header(analyst_token),
    )
    assert create_by_analyst.status_code == 403

    create_by_viewer = client.post(
        "/records",
        json=create_payload,
        headers=auth_header(viewer_token),
    )
    assert create_by_viewer.status_code == 403

    list_by_analyst = client.get("/records", headers=auth_header(analyst_token))
    assert list_by_analyst.status_code == 200
    assert len(list_by_analyst.json()) == 1

    list_by_viewer = client.get("/records", headers=auth_header(viewer_token))
    assert list_by_viewer.status_code == 403


def test_summary_endpoint_returns_aggregates(client):
    register_user(client, "admin@test.com", "password123", "admin")
    register_user(client, "viewer@test.com", "password123", "viewer")

    admin_token = login_token(client, "admin@test.com", "password123")
    viewer_token = login_token(client, "viewer@test.com", "password123")

    income_payload = {
        "amount": 1000,
        "type": "income",
        "category": "Salary",
        "date": date(2026, 4, 1).isoformat(),
        "notes": "Salary",
    }
    expense_payload = {
        "amount": 300,
        "type": "expense",
        "category": "Rent",
        "date": date(2026, 4, 2).isoformat(),
        "notes": "Monthly rent",
    }

    assert client.post("/records", json=income_payload, headers=auth_header(admin_token)).status_code == 201
    assert client.post("/records", json=expense_payload, headers=auth_header(admin_token)).status_code == 201

    summary_resp = client.get("/dashboard/summary", headers=auth_header(viewer_token))
    assert summary_resp.status_code == 200

    summary = summary_resp.json()
    assert summary["total_income"] == 1000
    assert summary["total_expenses"] == 300
    assert summary["net_balance"] == 700
    assert len(summary["recent_records"]) == 2
    assert any(item["category"] == "Salary" for item in summary["by_category_income"])
    assert any(item["category"] == "Rent" for item in summary["by_category_expense"])
