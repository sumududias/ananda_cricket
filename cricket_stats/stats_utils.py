from django.db.models import Count, Sum, Q, F, Case, When, Value, IntegerField, FloatField
from django.db.models.functions import Coalesce
from .models import Player, Match, MatchPlayer, BattingInnings, BowlingInnings

def get_player_stats_context(player, year=None, format_id=None):
    """
    Generate context dictionary with player statistics for the player profile view.
    
    Args:
        player: Player instance
        year: Optional year filter
        format_id: Optional match format filter
    
    Returns:
        dict: Context with player statistics
    """
    # Base querysets with optional filters
    match_filters = {}
    if year:
        match_filters['match__match_date__year'] = year
    if format_id:
        match_filters['match__format_id'] = format_id
    
    # Batting statistics
    batting_stats = MatchPlayer.objects.filter(
        player=player,
        batting_order__isnull=False,
        **match_filters
    ).aggregate(
        total_matches=Count('match', distinct=True),
        total_innings=Count('id', distinct=True),
        total_runs=Coalesce(Sum('runs_scored'), 0),
        total_balls=Coalesce(Sum('balls_faced'), 0),
        total_fours=Coalesce(Sum('fours'), 0),
        total_sixes=Coalesce(Sum('sixes'), 0),
        highest_score=Coalesce(Max('runs_scored'), 0),
        not_outs=Count('id', filter=Q(how_out__isnull=True) | Q(how_out='')),
        fifties=Count('id', filter=Q(runs_scored__gte=50, runs_scored__lt=100)),
        hundreds=Count('id', filter=Q(runs_scored__gte=100)),
        ducks=Count('id', filter=Q(runs_scored=0, batting_order__isnull=False, how_out__isnull=False)),
    )
    
    # Bowling statistics
    bowling_stats = MatchPlayer.objects.filter(
        player=player,
        overs_bowled__gt=0,
        **match_filters
    ).aggregate(
        total_wickets=Coalesce(Sum('wickets_taken'), 0),
        total_overs=Coalesce(Sum('overs_bowled'), 0),
        total_maidens=Coalesce(Sum('maidens'), 0),
        total_runs_conceded=Coalesce(Sum('runs_conceded'), 0),
        total_wides=Coalesce(Sum('wide_balls'), 0),
        total_noballs=Coalesce(Sum('no_balls'), 0),
        best_bowling=Max(
            Case(
                When(wickets_taken__gt=0, then=F('wickets_taken') * 1000 - F('runs_conceded')),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
    )
    
    # Calculate derived statistics
    # Batting average
    dismissals = batting_stats['total_innings'] - batting_stats['not_outs']
    batting_average = round(batting_stats['total_runs'] / dismissals, 2) if dismissals > 0 else 0
    
    # Batting strike rate
    batting_strike_rate = round((batting_stats['total_runs'] / batting_stats['total_balls']) * 100, 2) if batting_stats['total_balls'] > 0 else 0
    
    # Bowling average
    bowling_average = round(bowling_stats['total_runs_conceded'] / bowling_stats['total_wickets'], 2) if bowling_stats['total_wickets'] > 0 else 0
    
    # Bowling economy
    total_overs = float(bowling_stats['total_overs'] or 0)
    bowling_economy = round(bowling_stats['total_runs_conceded'] / total_overs, 2) if total_overs > 0 else 0
    
    # Bowling strike rate
    balls_bowled = int(total_overs) * 6 + int((total_overs % 1) * 10)
    bowling_strike_rate = round(balls_bowled / bowling_stats['total_wickets'], 2) if bowling_stats['total_wickets'] > 0 else 0
    
    # Best bowling
    best_bowling = None
    if bowling_stats['best_bowling'] and bowling_stats['best_bowling'] > 0:
        wickets = bowling_stats['best_bowling'] // 1000
        runs = bowling_stats['best_bowling'] % 1000
        best_bowling = f"{wickets}/{runs}"
    
    return {
        'batting': {
            'matches': batting_stats['total_matches'],
            'innings': batting_stats['total_innings'],
            'not_outs': batting_stats['not_outs'],
            'runs': batting_stats['total_runs'],
            'highest_score': batting_stats['highest_score'],
            'average': batting_average,
            'strike_rate': batting_strike_rate,
            'fours': batting_stats['total_fours'],
            'sixes': batting_stats['total_sixes'],
            'fifties': batting_stats['fifties'],
            'hundreds': batting_stats['hundreds'],
            'ducks': batting_stats['ducks'],
        },
        'bowling': {
            'wickets': bowling_stats['total_wickets'],
            'overs': total_overs,
            'maidens': bowling_stats['total_maidens'],
            'runs_conceded': bowling_stats['total_runs_conceded'],
            'wides': bowling_stats['total_wides'],
            'noballs': bowling_stats['total_noballs'],
            'best_bowling': best_bowling,
            'average': bowling_average,
            'economy': bowling_economy,
            'strike_rate': bowling_strike_rate,
        },
        'fielding': {
            'catches': MatchPlayer.objects.filter(
                player=player,
                **match_filters
            ).aggregate(
                catches=Coalesce(Sum('catches'), 0),
                stumpings=Coalesce(Sum('stumpings'), 0),
                runouts=Coalesce(Sum('runouts'), 0),
            ),
        },
        'year': year,
        'format_id': format_id,
    }