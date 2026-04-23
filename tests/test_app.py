import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test cases for the activities API endpoints"""

    def test_get_activities(self):
        """Test GET /activities returns all activities"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Check that we get a dictionary with activity names as keys
        assert isinstance(data, dict)
        assert len(data) > 0

        # Check that each activity has the expected structure
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@student.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the student was added to participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        activity_name = "NonExistent Activity"
        email = "test@student.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self):
        """Test signup when student is already signed up"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # This email is already in the participants

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # This email is in participants

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the student was removed from participants
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        # Arrange
        activity_name = "NonExistent Activity"
        email = "test@student.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregister when student is not signed up"""
        # Arrange
        activity_name = "Basketball Team"
        email = "notsignedup@student.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_root_redirect(self):
        """Test GET / redirects to static/index.html"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"