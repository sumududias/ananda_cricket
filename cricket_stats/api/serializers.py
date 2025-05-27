from rest_framework import serializers
from ..models import Player, Match, MatchPlayer, Team

class PlayerSerializer(serializers.ModelSerializer):
    batting_stats = serializers.SerializerMethodField()
    bowling_stats = serializers.SerializerMethodField()
    fielding_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'dob', 'batting_style', 'bowling_style', 'batting_stats', 'bowling_stats', 'fielding_stats']
    
    def get_batting_stats(self, obj):
        stats = obj.batting_stats
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
        stats = obj.bowling_stats
        if not stats:
            return None
        return {
            'matches': stats.get('matches', 0),
            'innings': stats.get('innings', 0),
            'overs': stats.get('overs', 0),
            'runs': stats.get('runs', 0),
            'wickets': stats.get('wickets', 0),
            'maidens': stats.get('maidens', 0),
            'wides': stats.get('wides', 0),
            'no_balls': stats.get('no_balls', 0),
            'average': stats.get('average', 0.0),
            'economy': stats.get('economy', 0.0),
            'best_bowling': stats.get('best_bowling', '0/0')
        }
    
    def get_fielding_stats(self, obj):
        stats = obj.fielding_stats
        if not stats:
            return None
        return {
            'matches': stats.get('matches', 0),
            'catches': stats.get('catches', 0),
            'stumpings': stats.get('stumpings', 0),
            'runouts': stats.get('runouts', 0)
        }

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class MatchPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    match = MatchSerializer()
    class Meta:
        model = MatchPlayer
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = '__all__'