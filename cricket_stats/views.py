from rest_framework import viewsets
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Sum
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

def player_profile(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    
    # Get basic stats
    batting_stats = player.batting_stats
    bowling_stats = player.bowling_stats
    fielding_stats = player.fielding_stats
    
    # Get centuries and half-centuries count
    match_stats = MatchPlayer.objects.filter(player=player)
    centuries = match_stats.filter(is_century=True).count()
    half_centuries = match_stats.filter(is_half_century=True).count()
    
    # Get total wide balls and no balls
    total_wide_balls = match_stats.aggregate(Sum('wide_balls'))['wide_balls__sum'] or 0
    total_no_balls = match_stats.aggregate(Sum('no_balls'))['no_balls__sum'] or 0
    
    # Get format-specific stats
    test_stats = player.get_stats_by_format('TEST')
    odi_stats = player.get_stats_by_format('ODI')
    t20_stats = player.get_stats_by_format('T20')
    
    context = {
        'player': player,
        'batting_stats': batting_stats,
        'bowling_stats': bowling_stats,
        'fielding_stats': fielding_stats,
        'centuries': centuries,
        'half_centuries': half_centuries,
        'total_wide_balls': total_wide_balls,
        'total_no_balls': total_no_balls,
        'test_stats': test_stats,
        'odi_stats': odi_stats,
        't20_stats': t20_stats,
    }
    
    return render(request, 'cricket_stats/player_profile.html', context)