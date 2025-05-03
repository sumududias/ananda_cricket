from rest_framework import serializers
from ..models import Player, Match, MatchPlayer, Team

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

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