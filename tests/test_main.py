import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from main import app, get_db

TEST_DB = "test_sunmate.db"

def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    connection = sqlite3.connect(TEST_DB , check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE batteryData (timestamp TEXT NOT NULL, soc INTEGER NOT NULL)""")

    cursor.execute("""CREATE TABLE energyConsumptionData (timestamp TEXT NOT NULL, consumption_kwh REAL NOT NULL)""")

    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T00:00:00", 85))
    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T06:00:00", 40))
    cursor.execute("INSERT INTO batteryData VALUES (?, ?)", ("2024-11-29T12:00:00", 70))

    cursor.execute("INSERT INTO energyConsumptionData VALUES (?, ?)", ("2024-11-29T00:00:00", 3.5))
    cursor.execute("INSERT INTO energyConsumptionData VALUES (?, ?)", ("2024-11-29T01:00:00", 4.2))

    connection.commit()
    connection.close()

def override_get_db():
    connection = sqlite3.connect(TEST_DB, check_same_thread=False)
    cursor = connection.cursor()
    try:
        yield connection, cursor
    finally:
        connection.close()

@pytest.fixture
def client():
    setup_test_db()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

class TestBatteryData:
    def test_get(self, client):
        response = client.get("/battery/soc")
        assert response.status_code == 200
        data = response.json()
        assert data["timestamp"] == "2024-11-29T12:00:00"
        assert data["soc"] == 70

    def test_post_ok(self, client):
        new_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "2024-11-30T06:00:00", "soc": 50},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=new_data)
        assert response.status_code == 200
        data = response.json()
        assert data["lowest_soc"] == 50
        assert data["highest_soc"] == 90
        assert data["soc_difference"] == 40

    def test_post_invalid_soc(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "2024-11-30T06:00:00", "soc": "invalid"},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

    def test_post_invalid_timestamp(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "invalid-timestamp", "soc": 50},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

    def test_post_big_soc(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "2024-11-30T06:00:00", "soc": 150},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

    def test_post_negative_soc(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "2024-11-30T06:00:00", "soc": -10},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

    def test_post_missing_soc(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"timestamp": "2024-11-30T06:00:00"},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

    def test_post_missing_timestamp(self, client):
        invalid_data = [
            {"timestamp": "2024-11-30T00:00:00", "soc": 90},
            {"soc": 50},
            {"timestamp": "2024-11-30T12:00:00", "soc": 80}
        ]
        response = client.post("/battery/daily", json=invalid_data)
        assert response.status_code == 422

class TestEnergyConsumptionData:
    def test_get_ok(self, client):
        response = client.get("/energy/consumption")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["hour"] == "00:00"
        assert data[0]["consumption_kwh"] == 3.5
        assert data[1]["hour"] == "01:00"
        assert data[1]["consumption_kwh"] == 4.2

    def test_post_ok(self, client):
        new_data = {"timestamp": "2024-11-30T00:00:00", "consumption_kwh": 5.0}
        response = client.post("/energy/consumption", json=new_data)
        assert response.status_code == 200

        response = client.get("/energy/consumption")
        data = response.json()
        assert any(entry["hour"] == "00:00" and entry["consumption_kwh"] == 5.0 for entry in data)

    def test_post_invalid_consumption(self, client):
        invalid_data = {"timestamp": "2024-11-30T00:00:00", "consumption_kwh": "invalid"}
        response = client.post("/energy/consumption", json=invalid_data)
        assert response.status_code == 422

    def test_post_invalid_timestamp(self, client):
        invalid_data = {"timestamp": "invalid-timestamp", "consumption_kwh": 5.0}
        response = client.post("/energy/consumption", json=invalid_data)
        assert response.status_code == 422