from __future__ import annotations


def test_models_returns_gateway_model(client, auth_headers) -> None:
    response = client.get("/v1/models", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "list"
    assert body["data"][0]["id"] == "yolo-cpu-detector"
    assert body["data"][0]["object"] == "model"
    assert body["data"][0]["owned_by"] == "local"
