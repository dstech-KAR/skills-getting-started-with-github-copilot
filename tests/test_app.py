import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Define initial activities for resetting
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interscholastic games",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Volleyball Club": {
        "description": "Learn volleyball skills and compete in friendly matches",
        "schedule": "Tuesdays, Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["jessica@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["sophia@mergington.edu"]
    },
    "Music Band": {
        "description": "Learn to play musical instruments and perform in concerts",
        "schedule": "Mondays, Fridays, 3:45 PM - 4:45 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and critical thinking skills through competitive debate",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts through hands-on activities",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["isabella@mergington.edu", "mason@mergington.edu"]
    }
}

@pytest.fixture
def client():
    """Fixture for FastAPI TestClient."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities dict before each test for isolation."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

# Tests for root redirect
def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200  # In test environment, static file is served directly
    # Alternatively, could check for redirect, but static mount may override

# Tests for GET /activities
def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert len(data["Chess Club"]["participants"]) == 2

# Tests for POST /activities/{name}/signup
def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "new@student.edu"})
    assert response.status_code == 200
    assert "Signed up new@student.edu for Chess Club" == response.json()["message"]
    # Verify added
    response = client.get("/activities")
    assert "new@student.edu" in response.json()["Chess Club"]["participants"]

def test_signup_invalid_activity(client):
    response = client.post("/activities/Invalid Activity/signup", params={"email": "test@test.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_duplicate(client):
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "dup@test.com"})
    # Duplicate attempt
    response = client.post("/activities/Chess Club/signup", params={"email": "dup@test.com"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

# Tests for DELETE /activities/{name}/signup
def test_unregister_success(client):
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "unreg@test.com"})
    # Then unregister
    response = client.delete("/activities/Chess Club/signup", params={"email": "unreg@test.com"})
    assert response.status_code == 200
    assert "Unregistered unreg@test.com from Chess Club" == response.json()["message"]
    # Verify removed
    response = client.get("/activities")
    assert "unreg@test.com" not in response.json()["Chess Club"]["participants"]

def test_unregister_invalid_activity(client):
    response = client.delete("/activities/Invalid Activity/signup", params={"email": "test@test.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Chess Club/signup", params={"email": "notsigned@test.com"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"