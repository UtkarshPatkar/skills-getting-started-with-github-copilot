"""
Test suite for Mergington High School API

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
Each test is structured in three distinct sections:
- Arrange: Set up test data and preconditions
- Act: Execute the code under test
- Assert: Verify the expected outcomes
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


# Initial activities data for reset
INITIAL_ACTIVITIES = {
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
        "description": "Competitive basketball team for interscholastic play",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and compete in matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "sophia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in theatrical productions and develop acting skills",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["nina@mergington.edu"]
    },
    "Debate Team": {
        "description": "Compete in academic debate competitions",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 4:45 PM",
        "max_participants": 16,
        "participants": ["marcus@mergington.edu", "isabella@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science competitions and conduct experiments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["david@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Provide a TestClient instance for API testing"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Automatically reset activities data before each test.
    This fixture ensures tests don't affect each other through shared state.
    """
    # Arrange: Reset to initial state before each test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    # Cleanup: Reset after test (optional, but ensures consistency)
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


# ============================================================================
# Tests for GET /activities endpoint
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all available activities"""
    # Arrange
    # (Client and activities are set up by fixtures)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_has_correct_structure(client):
    """Test that activities have all required fields with correct types"""
    # Arrange
    # (Client and activities are set up by fixtures)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["description"], str)
    assert isinstance(chess_club["participants"], list)
    assert isinstance(chess_club["max_participants"], int)


def test_get_activities_includes_participants(client):
    """Test that activities include their participant lists"""
    # Arrange
    # (Client and activities are set up by fixtures)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


# ============================================================================
# Tests for POST /activities/{activity_name}/signup endpoint
# ============================================================================

def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert new_email in data["message"]
    assert new_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count + 1


def test_signup_activity_not_found(client):
    """Test signup fails with 404 when activity doesn't exist"""
    # Arrange
    non_existent_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{non_existent_activity}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_duplicate_participant(client):
    """Test signup fails with 400 when student is already registered"""
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already registered
    assert existing_email in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={existing_email}"
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_activity_full(client):
    """Test signup fails with 400 when activity has reached max capacity"""
    # Arrange: Fill Tennis Club to max capacity (10 participants)
    activity_name = "Tennis Club"
    max_participants = activities[activity_name]["max_participants"]
    # Fill remaining spots
    current_count = len(activities[activity_name]["participants"])
    for i in range(current_count, max_participants):
        activities[activity_name]["participants"].append(f"student{i}@mergington.edu")
    
    assert len(activities[activity_name]["participants"]) == max_participants
    new_email = "overflow@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "full" in data["detail"].lower()


def test_signup_with_spaces_in_activity_name(client):
    """Test signup works correctly with activity names containing spaces"""
    # Arrange
    activity_name = "Chess Club"  # Contains space
    new_email = "spacestest@mergington.edu"
    # URL encoding is handled by TestClient automatically

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]


def test_signup_with_special_chars_in_email(client):
    """Test signup accepts emails with special characters"""
    # Arrange
    activity_name = "Programming Class"
    special_email = "student.test@mergington.edu"  # Contains dot character

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={special_email}"
    )

    # Assert
    assert response.status_code == 200
    assert special_email in activities[activity_name]["participants"]


def test_signup_near_capacity(client):
    """Test signup succeeds when activity is not yet at capacity"""
    # Arrange: Tennis Club starts with 2 participants, max is 10
    activity_name = "Tennis Club"
    # Fill to max - 1
    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])
    for i in range(current_count, max_participants - 1):
        activities[activity_name]["participants"].append(f"filler{i}@mergington.edu")
    
    new_email = "lastspot@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == max_participants


# ============================================================================
# Tests for DELETE /activities/{activity_name}/participants endpoint
# ============================================================================

def test_delete_participant_success(client):
    """Test successful removal of a participant from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])
    assert email_to_remove in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={email_to_remove}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email_to_remove in data["message"]
    assert email_to_remove not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_delete_participant_activity_not_found(client):
    """Test delete fails with 404 when activity doesn't exist"""
    # Arrange
    non_existent_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{non_existent_activity}/participants?email={email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_participant_not_in_activity(client):
    """Test delete fails with 404 when participant is not registered"""
    # Arrange
    activity_name = "Chess Club"
    unregistered_email = "notregistered@mergington.edu"
    assert unregistered_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={unregistered_email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_with_url_encoding(client):
    """Test delete works correctly with URL-encoded parameters"""
    # Arrange
    activity_name = "Programming Class"
    email_to_remove = "emma@mergington.edu"
    assert email_to_remove in activities[activity_name]["participants"]
    # TestClient handles URL encoding automatically

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={email_to_remove}"
    )

    # Assert
    assert response.status_code == 200
    assert email_to_remove not in activities[activity_name]["participants"]


def test_delete_last_participant(client):
    """Test deleting the last participant from an activity"""
    # Arrange
    activity_name = "Basketball Team"
    # Basketball Team has only one participant initially
    last_participant = "alex@mergington.edu"
    assert len(activities[activity_name]["participants"]) == 1
    assert last_participant in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={last_participant}"
    )

    # Assert
    assert response.status_code == 200
    assert len(activities[activity_name]["participants"]) == 0
    assert last_participant not in activities[activity_name]["participants"]


def test_delete_and_re_signup(client):
    """Test that a participant can be removed and then sign up again"""
    # Arrange
    activity_name = "Drama Club"
    email = "grace@mergington.edu"
    assert email in activities[activity_name]["participants"]

    # Act: Delete
    delete_response = client.delete(
        f"/activities/{activity_name}/participants?email={email}"
    )

    # Assert: Deletion succeeded
    assert delete_response.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Act: Sign up again
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert: Signup succeeded
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]


# ============================================================================
# Edge case and integration tests
# ============================================================================

def test_multiple_activities_for_same_student(client):
    """Test that a student can sign up for multiple activities"""
    # Arrange
    student_email = "multitasker@mergington.edu"
    activities_to_join = ["Chess Club", "Drama Club", "Art Studio"]

    # Act & Assert
    for activity_name in activities_to_join:
        response = client.post(
            f"/activities/{activity_name}/signup?email={student_email}"
        )
        assert response.status_code == 200
        assert student_email in activities[activity_name]["participants"]

    # Final assertion: Student is in all three activities
    for activity_name in activities_to_join:
        assert student_email in activities[activity_name]["participants"]


def test_concurrent_signups_respect_capacity(client):
    """Test that capacity is enforced when multiple signups happen"""
    # Arrange: Create activity at max - 2 capacity
    activity_name = "Tennis Club"
    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])
    
    # Fill to max - 2
    for i in range(current_count, max_participants - 2):
        activities[activity_name]["participants"].append(f"filler{i}@mergington.edu")

    email1 = "concurrent1@mergington.edu"
    email2 = "concurrent2@mergington.edu"
    email3 = "concurrent3@mergington.edu"

    # Act: Sign up three students (only 2 spots available)
    response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
    response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")
    response3 = client.post(f"/activities/{activity_name}/signup?email={email3}")

    # Assert: First two succeed, third fails
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 400
    assert email1 in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]
    assert email3 not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == max_participants
