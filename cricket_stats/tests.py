from django.test import TestCase
from django.urls import reverse
from .models import Player, Team, Tournament, Match


class BasicModelTests(TestCase):
    """Basic tests for the cricket_stats models"""
    
    def setUp(self):
        # Create test data
        self.team = Team.objects.create(name="Test Team")
        
    def test_team_str(self):
        """Test the string representation of a Team"""
        self.assertEqual(str(self.team), "Test Team")


class ViewTests(TestCase):
    """Tests for the cricket_stats views"""
    
    def test_reports_dashboard(self):
        """Test that the reports dashboard loads"""
        url = reverse('cricket_stats:reports_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects to login
