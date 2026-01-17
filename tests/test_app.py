"""Tests for the Mergington High School Activities API"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test that activities can be retrieved"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_have_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, fresh_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_adds_participant(self, client, fresh_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate(self, client, fresh_activities):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, fresh_activities):
        """Test successful unregistration"""
        email = "michael@mergington.edu"
        
        # Verify they're in the activity
        activities_before = client.get("/activities").json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify they're removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after["Chess Club"]["participants"]
    
    def test_unregister_not_registered(self, client, fresh_activities):
        """Test unregistration of someone not in the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
