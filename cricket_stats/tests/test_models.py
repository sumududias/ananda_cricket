from django.test import TestCase
from django.core.exceptions import ValidationError
from cricket_stats.models import Player, Match, MatchPlayer
from datetime import date

class PlayerModelTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create(
            name="Test Player",
            date_of_birth=date(2000, 1, 1),
            jersey_number=7
        )

    def test_player_creation(self):
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.jersey_number, 7)

    def test_player_str(self):
        self.assertEqual(str(self.player), "Test Player")

    def test_invalid_jersey_number(self):
        with self.assertRaises(ValidationError):
            player = Player(name="Invalid", jersey_number=-1)
            player.full_clean()

class MatchModelTests(TestCase):
    def setUp(self):
        self.match = Match.objects.create(
            match_date=date.today(),
            venue="Test Ground",
            format="ODI",
            team="Ananda College",
            toss_winner="Ananda College",
            toss_decision="bat"
        )

    def test_match_creation(self):
        self.assertEqual(self.match.venue, "Test Ground")
        self.assertEqual(self.match.format, "ODI")

    def test_invalid_format(self):
        with self.assertRaises(ValidationError):
            match = Match(format="INVALID")
            match.full_clean()

    def test_innings_totals(self):
        self.assertEqual(self.match.first_innings_total, 0)
        self.assertEqual(self.match.second_innings_total, 0)

class MatchPlayerTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create(
            name="Test Player",
            date_of_birth=date(2000, 1, 1)
        )
        self.match = Match.objects.create(
            match_date=date.today(),
            venue="Test Ground"
        )
        self.match_player = MatchPlayer.objects.create(
            match=self.match,
            player=self.player,
            innings_number=1,
            batting_order=1,
            runs_scored=50,
            balls_faced=40
        )

    def test_match_player_creation(self):
        self.assertEqual(self.match_player.runs_scored, 50)
        self.assertEqual(self.match_player.balls_faced, 40)

    def test_batting_strike_rate(self):
        strike_rate = (self.match_player.runs_scored / self.match_player.balls_faced) * 100
        self.assertEqual(round(strike_rate, 2), 125.00)
