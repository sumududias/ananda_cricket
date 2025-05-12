from rest_framework import viewsets
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max
from django.db.models import Q
from .models import (
    Player, Match, Team, Tournament, 
    MatchPlayer, Substitution, TeamStanding,
    BattingInnings, BowlingInnings
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

def player_list(request):
    from datetime import date
    
    players = Player.objects.all()
    
    # Handle search query
    search_query = request.GET.get('q')
    age_group = request.GET.get('age_group')
    
    if search_query:
        players = players.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if age_group:
        today = date.today()
        if age_group == 'U13':
            max_age = 13
        elif age_group == 'U15':
            max_age = 15
        elif age_group == 'U17':
            max_age = 17
        elif age_group == 'U19':
            max_age = 19
        else:
            max_age = None
            
        if max_age:
            cutoff_date = date(today.year - max_age, today.month, today.day)
            min_date = date(today.year - (max_age - 2), today.month, today.day)
            players = players.filter(dob__gt=cutoff_date, dob__lte=min_date)
    
    # Order by name
    players = players.order_by('first_name', 'last_name')
    
    return render(request, 'cricket_stats/player_list.html', {'players': players})

def player_profile(request, player_id):
    """Display player profile and statistics."""
    player = get_object_or_404(Player, pk=player_id)
    
    # Get all match stats for the player
    match_stats = MatchPlayer.objects.filter(player=player, is_playing_xi=True)
    
    # Debug info
    print(f"Player: {player.first_name} {player.last_name}")
    print(f"Match stats count: {match_stats.count()}")
    
    # Helper function to calculate stats
    def calculate_stats(match_qs):
        # Debug info
        print(f"\nCalculating stats for query set:")
        print(f"Match stats: {match_qs.count()}")
        
        # Calculate batting stats
        batting_stats = {
            'matches': match_qs.values('match').distinct().count(),
            'innings': match_qs.filter(batting_order__isnull=False).count(),
            'runs': match_qs.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
            'balls_faced': match_qs.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0,
            'fours': match_qs.aggregate(Sum('fours'))['fours__sum'] or 0,
            'sixes': match_qs.aggregate(Sum('sixes'))['sixes__sum'] or 0,
            'highest_score': match_qs.aggregate(Max('runs_scored'))['runs_scored__max'] or 0,
            'hundreds': match_qs.filter(runs_scored__gte=100).count(),
            'fifties': match_qs.filter(runs_scored__gte=50, runs_scored__lt=100).count(),
        }
        
        # Calculate batting average and strike rate
        total_runs = batting_stats['runs']
        total_balls = batting_stats['balls_faced']
        not_outs = match_qs.filter(batting_order__isnull=False).filter(Q(how_out='') | Q(how_out__isnull=True)).count()
        total_innings = batting_stats['innings']
        total_dismissals = total_innings - not_outs
        
        batting_stats['average'] = round(total_runs / total_dismissals, 2) if total_dismissals > 0 else total_runs
        batting_stats['strike_rate'] = round((total_runs / total_balls * 100), 2) if total_balls > 0 else 0
        
        # Debug info
        print("\nBatting stats:")
        print(f"Total runs: {total_runs}")
        print(f"Total balls: {total_balls}")
        print(f"Not outs: {not_outs}")
        print(f"Total innings: {total_innings}")
        print(f"Average: {batting_stats['average']}")
        print(f"Strike rate: {batting_stats['strike_rate']}")
        
        # Calculate bowling stats
        bowling_stats = {
            'wickets': match_qs.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0,
            'overs': match_qs.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0,
            'runs_conceded': match_qs.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] or 0,
            'maidens': match_qs.aggregate(Sum('maidens'))['maidens__sum'] or 0,
            'wides': match_qs.aggregate(Sum('wide_balls'))['wide_balls__sum'] or 0,
            'no_balls': match_qs.aggregate(Sum('no_balls'))['no_balls__sum'] or 0,
            'five_wickets': match_qs.filter(wickets_taken__gte=5).count(),
        }
        
        # Calculate bowling averages
        total_wickets = bowling_stats['wickets']
        total_runs = bowling_stats['runs_conceded']
        total_overs = bowling_stats['overs']
        
        bowling_stats['average'] = round(total_runs / total_wickets, 2) if total_wickets > 0 else 0
        bowling_stats['economy'] = round(total_runs / total_overs, 2) if total_overs > 0 else 0
        bowling_stats['strike_rate'] = round((total_overs * 6) / total_wickets, 2) if total_wickets > 0 else 0
        
        # Debug info
        print("\nBowling stats:")
        print(f"Total wickets: {total_wickets}")
        print(f"Total runs conceded: {total_runs}")
        print(f"Total overs: {total_overs}")
        print(f"Average: {bowling_stats['average']}")
        print(f"Economy: {bowling_stats['economy']}")
        print(f"Strike rate: {bowling_stats['strike_rate']}")
        
        # Calculate fielding stats
        fielding_stats = {
            'catches': match_qs.aggregate(Sum('catches'))['catches__sum'] or 0,
            'stumpings': match_qs.aggregate(Sum('stumpings'))['stumpings__sum'] or 0,
            'runouts': match_qs.aggregate(Sum('runouts'))['runouts__sum'] or 0,
            'total_dismissals': 0  # Will be calculated below
        }
        fielding_stats['total_dismissals'] = (
            fielding_stats['catches'] + 
            fielding_stats['stumpings'] + 
            fielding_stats['runouts']
        )
        
        # Debug info
        print("\nFielding stats:")
        print(f"Catches: {fielding_stats['catches']}")
        print(f"Stumpings: {fielding_stats['stumpings']}")
        print(f"Runouts: {fielding_stats['runouts']}")
        print(f"Total dismissals: {fielding_stats['total_dismissals']}")
        
        return {
            'batting': batting_stats, 
            'bowling': bowling_stats,
            'fielding': fielding_stats
        }
    
    # Calculate stats for different formats
    context = {
        'player': player,
        'overall_stats': calculate_stats(match_stats),
        'test_stats': calculate_stats(match_stats.filter(match__match_format='TEST')),
        'odi_stats': calculate_stats(match_stats.filter(match__match_format='ODI')),
        't20_stats': calculate_stats(match_stats.filter(match__match_format='T20')),
    }
    
    return render(request, 'cricket_stats/player_profile.html', context)

def home(request):
    """Home page view."""
    return render(request, 'cricket_stats/home.html', {
        'title': 'Welcome to Ananda Cricket'
    })