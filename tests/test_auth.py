from __future__ import annotations


def test_missing_api_key_returns_401(client) -> None:
    response = client.get("/v1/models")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_wrong_api_key_returns_401(client) -> None:
    response = client.get("/v1/models", headers={"Authorization": "Bearer wrong-key"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"


def test_correct_api_key_allows_request(client, auth_headers) -> None:
    response = client.get("/v1/models", headers=auth_headers)

    assert response.status_code == 200
