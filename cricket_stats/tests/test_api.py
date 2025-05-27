from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from cricket_stats.models import Player, Match, MatchPlayer
from datetime import date
import json

class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        self.player = Player.objects.create(
            name="Test Player",
            date_of_birth=date(2000, 1, 1),
            jersey_number=7
        )
        self.match = Match.objects.create(
            match_date=date.today(),
            venue="Test Ground",
            format="ODI"
        )

    def test_player_list(self):
        response = self.client.get('/api/players/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_player_detail(self):
        response = self.client.get(f'/api/players/{self.player.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Player")

    def test_create_player(self):
        data = {
            'name': 'New Player',
            'date_of_birth': '2000-01-01',
            'jersey_number': 10
        }
        response = self.client.post(
            '/api/players/',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Player.objects.count(), 2)

    def test_match_list(self):
        response = self.client.get('/api/matches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_match(self):
        data = {
            'match_date': str(date.today()),
            'venue': 'New Ground',
            'format': 'T20',
            'team': 'Ananda College',
            'toss_winner': 'Ananda College',
            'toss_decision': 'bat'
        }
        response = self.client.post(
            '/api/matches/',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.count(), 2)

    def test_add_player_to_match(self):
        data = {
            'player': self.player.pk,
            'innings_number': 1,
            'batting_order': 1,
            'runs_scored': 50,
            'balls_faced': 40
        }
        response = self.client.post(
            f'/api/matches/{self.match.pk}/add-player/',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MatchPlayer.objects.count(), 1)
