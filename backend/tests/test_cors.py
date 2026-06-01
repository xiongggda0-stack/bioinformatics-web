from fastapi.testclient import TestClient


def test_cors_allows_local_preview_origin(client: TestClient) -> None:
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:3001"},
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:3001"
