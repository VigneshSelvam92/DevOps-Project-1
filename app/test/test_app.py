import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_home_status_code(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_returns_expected_keys(client):
    response = client.get("/")
    data = response.get_json()
    assert "message" in data
    assert "version" in data
    assert "hostname" in data


def test_home_default_version(client):
    response = client.get("/")
    data = response.get_json()
    assert data["version"] == "v1.0.0"


def test_healthz_status_code(client):
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_body(client):
    response = client.get("/healthz")
    data = response.get_json()
    assert data["status"] == "ok"