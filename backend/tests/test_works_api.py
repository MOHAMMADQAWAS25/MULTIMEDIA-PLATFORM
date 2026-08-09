from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import create_app


def test_submit_work_starts_pending() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/works",
        json={
            "title": "Campus Poster",
            "description": "A digital poster for a university event.",
            "category": "digital_art",
            "owner_id": str(uuid4()),
            "tags": ["poster", "campus"],
            "file_url": "uploads/campus-poster.png",
            "downloads_allowed": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["title"] == "Campus Poster"


def test_public_list_only_shows_approved_works() -> None:
    client = TestClient(create_app())
    create_response = client.post(
        "/api/v1/works",
        json={
            "title": "Motion Intro",
            "description": "Short animation intro.",
            "category": "animation",
            "owner_id": str(uuid4()),
            "tags": ["motion"],
            "file_url": "uploads/motion-intro.mp4",
            "downloads_allowed": False,
        },
    )
    work_id = create_response.json()["id"]

    assert client.get("/api/v1/works").json() == []

    approve_response = client.post(f"/api/v1/works/{work_id}/approve", json={})

    assert approve_response.status_code == 200
    public_works = client.get("/api/v1/works").json()
    assert len(public_works) == 1
    assert public_works[0]["id"] == work_id
