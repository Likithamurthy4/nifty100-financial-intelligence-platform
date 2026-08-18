from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_all_sectors():
    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 10
    assert len(data["sectors"]) == 10


def test_information_technology_companies():
    response = client.get("/api/v1/sectors/Information%20Technology/companies")

    assert response.status_code == 200

    data = response.json()

    assert data["sector"] == "Information Technology"
    assert data["count"] > 0

    for company in data["companies"]:
        assert company["broad_sector"].lower() == "information technology"
