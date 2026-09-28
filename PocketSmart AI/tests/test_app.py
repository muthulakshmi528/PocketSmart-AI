from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home_page():

    response = client.get("/")

    assert response.status_code == 200

    assert "PocketSmart AI" in response.text


def test_home_fallback_api():

    payload = {

        "budget": 20000,

        "rooms": [
            "Living Room"
        ],

        "style": "Modern",

        "city": "Coimbatore",

        "items": [
            {
                "category": "lighting",
                "quantity": 1
            }
        ]

    }


    response = client.post(
        "/api/generate-home",
        json=payload,
    )


    assert response.status_code == 200


    data = response.json()


    assert data["planner"] == "home"

    assert data["budget"] == 20000

    assert "recommendations" in data


def test_party_api():

    payload = {

        "budget": 15000,

        "guests": 20,

        "event_type": "Birthday",

        "venue": "Home",

        "city": "Coimbatore",

        "preferences": "simple"

    }


    response = client.post(
        "/api/generate-party",
        json=payload,
    )


    assert response.status_code == 200

    assert (
        response.json()["planner"]
        == "party"
    )