from rest_framework import serializers
from .models import (
    Player, Match, Team, Tournament,
    MatchPlayer, Substitution, TeamStanding,
    BattingInnings, BowlingInnings
)

class PlayerSerializer(serializers.ModelSerializer):
    batting_stats = serializers.SerializerMethodField()
    bowling_stats = serializers.SerializerMethodField()
    fielding_stats = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = '__all__'

    def get_batting_stats(self, obj):
        stats = obj.get_batting_stats()
        if not stats:
            return None
        return {
            'matches': stats.get('matches', 0),
            'innings': stats.get('innings', 0),
            'not_outs': stats.get('not_outs', 0),
            'runs': stats.get('runs', 0),
            'balls_faced': stats.get('balls_faced', 0),
            'average': stats.get('average', 0.0),
            'strike_rate': stats.get('strike_rate', 0.0),
            'highest_score': stats.get('highest_score', 0),
            'fours': stats.get('fours', 0),
            'sixes': stats.get('sixes', 0)
        }

    def get_bowling_stats(self, obj):
        stats = obj.get_bowling_stats()
        if not stats:
            return None
        return {
            'matches': stats.get('matches', 0),
            'innings': stats.get('innings', 0),
            'overs': stats.get('overs', 0),
            'runs': stats.get('runs', 0),
            'wickets': stats.get('wickets', 0),
            'average': stats.get('average', 0.0),
            'economy': stats.get('economy', 0.0),
            'strike_rate': stats.get('strike_rate', 0.0),
            'best_bowling': stats.get('best_bowling', '0/0')
        }

    def get_fielding_stats(self, obj):
        stats = obj.get_fielding_stats()
        if not stats:
            return None
        return {
            'matches': stats.get('matches', 0),
            'catches': stats.get('catches', 0),
            'stumpings': stats.get('stumpings', 0),
            'runouts': stats.get('runouts', 0)
        }

class MatchPlayerSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()

    class Meta:
        model = MatchPlayer
        fields = '__all__'

    def get_player_name(self, obj):
        return str(obj.player) if obj.player else None

class MatchSerializer(serializers.ModelSerializer):
    players = MatchPlayerSerializer(source='matchplayer_set', many=True, read_only=True)
    man_of_match_name = serializers.SerializerMethodField()
    tournament_name = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = '__all__'

    def get_man_of_match_name(self, obj):
        return str(obj.man_of_match) if obj.man_of_match else None

    def get_tournament_name(self, obj):
        if obj.tournament:
            return obj.tournament.name
        return None

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'

class SubstitutionSerializer(serializers.ModelSerializer):
    player_out_name = serializers.SerializerMethodField()
    player_in_name = serializers.SerializerMethodField()

    class Meta:
        model = Substitution
        fields = '__all__'

    def get_player_out_name(self, obj):
        return str(obj.player_out) if obj.player_out else None

    def get_player_in_name(self, obj):
        return str(obj.player_in) if obj.player_in else None

class TeamStandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamStanding
        fields = '__all__'

class BattingInningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattingInnings
        fields = '__all__'

class BowlingInningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BowlingInnings
        fields = '__all__'