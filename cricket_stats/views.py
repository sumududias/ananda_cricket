from rest_framework import viewsets
from .models import (
    Player, Match, Team, Tournament, 
    MatchPlayer, Substitution, TeamStanding
)
from .serializers import (
    PlayerSerializer, MatchSerializer, TeamSerializer,
    TournamentSerializer, MatchPlayerSerializer,
    SubstitutionSerializer, TeamStandingSerializer
)

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.prefetch_related(
        'matchplayer_set',
        'matchplayer_set__player'
    ).select_related(
        'tournament',
        'man_of_match'
    ).all()
    serializer_class = MatchSerializer

    def get_queryset(self):
        return Match.objects.prefetch_related(
            'matchplayer_set',
            'matchplayer_set__player'
        ).select_related(
            'tournament',
            'man_of_match'
        ).all()

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class MatchPlayerViewSet(viewsets.ModelViewSet):
    queryset = MatchPlayer.objects.all()
    serializer_class = MatchPlayerSerializer

class SubstitutionViewSet(viewsets.ModelViewSet):
    queryset = Substitution.objects.all()
    serializer_class = SubstitutionSerializer

class TeamStandingViewSet(viewsets.ModelViewSet):
    queryset = TeamStanding.objects.all()
    serializer_class = TeamStandingSerializer