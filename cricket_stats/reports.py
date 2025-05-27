from django.db.models import Count, Sum, Q, F, Avg, Max
from django.db.models.functions import ExtractYear, TruncDate
from django.utils import timezone
from .models import Player, Match, MatchPlayer, PlayerAttendance, MatchFormat, TrainingSession
from datetime import datetime, timedelta

def generate_attendance_report(start_date=None, end_date=None, player_id=None, match_format=None):
    """
    Generate attendance report with filters
    """
    queryset = PlayerAttendance.objects.select_related('player', 'match', 'reported_by')
    
    # Apply filters
    if start_date:
        queryset = queryset.filter(match__match_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(match__match_date__lte=end_date)
    if player_id:
        queryset = queryset.filter(player_id=player_id)
    if match_format:
        queryset = queryset.filter(match__format_id=match_format)
    
    # Group by player and status
    return queryset.values(
        'player__id',
        'player__first_name',
        'player__last_name',
        'status'
    ).annotate(
        count=Count('id')
    ).order_by('player__first_name', 'player__last_name')

def get_player_performance_summary(player_id, year=None, format_id=None):
    """
    Get detailed performance summary for a player
    """
    queryset = MatchPlayer.objects.filter(player_id=player_id)
    
    if year:
        queryset = queryset.filter(match__match_date__year=year)
    if format_id:
        queryset = queryset.filter(match__format_id=format_id)
    
    # Get basic stats
    stats = queryset.aggregate(
        total_matches=Count('id', distinct=True),
        total_runs=Sum('runs_scored'),
        total_wickets=Sum('wickets_taken'),
        total_catches=Sum('catches'),
        total_stumpings=Sum('stumpings')
    )
    
    # Get batting stats
    batting_stats = queryset.aggregate(
        highest_score=Max('runs_scored'),
        batting_avg=Avg('runs_scored'),
        strike_rate=Avg('strike_rate'),
        fifties=Count('id', filter=Q(runs_scored__gte=50) & Q(runs_scored__lt=100)),
        hundreds=Count('id', filter=Q(runs_scored__gte=100))
    )
    
    # Get bowling stats
    bowling_stats = queryset.aggregate(
        bowling_avg=Avg('runs_conceded') / F('wickets_taken'),
        economy=Avg('economy'),
        best_bowling=Max('wickets_taken'),
        five_wickets=Count('id', filter=Q(wickets_taken__gte=5))
    )
    
    return {
        'basic': stats,
        'batting': batting_stats,
        'bowling': bowling_stats
    }

def get_team_performance_report(team_name, season_year=None):
    """
    Generate team performance report
    """
    queryset = Match.objects.filter(team=team_name)
    
    if season_year:
        queryset = queryset.filter(match_date__year=season_year)
    
    # Get match results
    results = queryset.values('result').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get player contributions
    top_batsmen = MatchPlayer.objects.filter(
        match__in=queryset
    ).values(
        'player__first_name', 'player__last_name'
    ).annotate(
        total_runs=Sum('runs_scored'),
        avg=Avg('runs_scored'),
        highest=Max('runs_scored')
    ).order_by('-total_runs')[:5]
    
    top_bowlers = MatchPlayer.objects.filter(
        match__in=queryset,
        overs_bowled__gt=0
    ).values(
        'player__first_name', 'player__last_name'
    ).annotate(
        total_wickets=Sum('wickets_taken'),
        avg=Avg('runs_conceded') / F('wickets_taken'),
        economy=Avg('economy')
    ).order_by('-total_wickets')[:5]
    
    return {
        'match_results': list(results),
        'top_batsmen': list(top_batsmen),
        'top_bowlers': list(top_bowlers)
    }

def get_season_summary(year=None):
    """
    Generate season summary report
    """
    if not year:
        year = timezone.now().year
    
    matches = Match.objects.filter(match_date__year=year)
    players = Player.objects.filter(
        matchplayer__match__in=matches
    ).distinct()
    
    # Get match stats
    match_stats = matches.aggregate(
        total_matches=Count('id'),
        matches_completed=Count('id', filter=~Q(result='')),
        matches_won=Count('id', filter=Q(result__icontains='won')),
        matches_lost=Count('id', filter=Q(result__icontains='lost'))
    )
    
    # Get player stats
    player_stats = players.annotate(
        matches_played=Count('matchplayer', filter=Q(matchplayer__match__in=matches)),
        runs=Sum('matchplayer__runs_scored', filter=Q(matchplayer__match__in=matches)),
        wickets=Sum('matchplayer__wickets_taken', filter=Q(matchplayer__match__in=matches))
    ).order_by('-runs')[:10]
    
    return {
        'year': year,
        'match_stats': match_stats,
        'top_players': list(player_stats)
    }

def get_player_attendance_summary(player_id):
    """
    Get attendance summary for a player
    """
    attendances = PlayerAttendance.objects.filter(player_id=player_id)
    
    if not attendances.exists():
        return None
    
    total_matches = Match.objects.count()
    attendance_stats = attendances.aggregate(
        present=Count('id', filter=Q(status='P')),
        absent=Count('id', filter=Q(status='A')),
        late=Count('id', filter=Q(status='L')),
        excused=Count('id', filter=Q(status='E'))
    )
    
    attendance_stats['total_matches'] = total_matches
    attendance_stats['attendance_percentage'] = round(
        (attendance_stats['present'] / total_matches * 100) if total_matches > 0 else 0,
        2
    )
    
    return attendance_stats

def generate_attendance_report(start_date=None, end_date=None, age_group=None, player_class=None):
    """
    Generate attendance report with filters for training sessions only
    """
    from django.db.models import Count, Q, Sum, Case, When, IntegerField, F
    
    # Start with all players
    players = Player.objects.filter(is_active=True)
    
    # Apply filters
    if player_class:
        players = players.filter(player_class=player_class)
    
    # For age group filtering (since it's a property)
    if age_group:
        filtered_players = []
        for player in players:
            if player.age_group == age_group:
                filtered_players.append(player.id)
        players = players.filter(id__in=filtered_players)
    
    # Get all training sessions
    training_sessions = TrainingSession.objects.all()
    
    # Apply date filters
    if start_date:
        training_sessions = training_sessions.filter(date__gte=start_date)
    if end_date:
        training_sessions = training_sessions.filter(date__lte=end_date)
    
    # Create report data
    report_data = {}
    
    # For each player, get their attendance records
    for player in players:
        # Get attendance records for this player
        attendance_records = PlayerAttendance.objects.filter(
            player=player,
            training_session__in=training_sessions
        )
        
        # Count by status
        present_count = attendance_records.filter(status='P').count()
        absent_count = attendance_records.filter(status='A').count()
        excused_count = attendance_records.filter(status='E').count()
        late_count = attendance_records.filter(status='L').count()
        
        # Calculate attendance rate
        total_sessions = present_count + absent_count + excused_count + late_count
        if total_sessions > 0:
            attendance_rate = (present_count + late_count) / total_sessions * 100
        else:
            attendance_rate = 0
        
        # Only add to report if there are attendance records
        report_data[player.id] = {
            'name': f"{player.first_name} {player.last_name}",
            'present': present_count,
            'absent': absent_count,
            'excused': excused_count,
            'late': late_count,
            'attendance_rate': attendance_rate
        }
    
    return report_data

def generate_audit_report(start_date=None, end_date=None, user_id=None, content_type=None):
    """
    Generate an audit report showing user actions within a date range.
    
    Parameters:
    - start_date: Optional start date for filtering
    - end_date: Optional end date for filtering
    - user_id: Optional user ID to filter actions by specific user
    - content_type: Optional content type to filter actions (e.g., 'player', 'match')
    
    Returns a dictionary with audit log entries
    """
    from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
    from django.contrib.contenttypes.models import ContentType
    from django.utils import timezone
    from datetime import timedelta
    from django.contrib.auth.models import User
    
    # Set default date range if not provided
    if not end_date:
        end_date = timezone.now()
    if not start_date:
        start_date = end_date - timedelta(days=7)  # Default to last 7 days
    
    # Start with all log entries in the date range
    log_entries = LogEntry.objects.filter(
        action_time__gte=start_date,
        action_time__lte=end_date
    ).select_related('user', 'content_type')
    
    # Apply filters
    if user_id:
        log_entries = log_entries.filter(user_id=user_id)
    
    if content_type:
        ct = ContentType.objects.filter(model__iexact=content_type).first()
        if ct:
            log_entries = log_entries.filter(content_type=ct)
    
    # Format the log entries for the report
    formatted_entries = []
    for entry in log_entries:
        action_type = {
            ADDITION: 'Added',
            CHANGE: 'Changed',
            DELETION: 'Deleted'
        }.get(entry.action_flag, 'Unknown')
        
        formatted_entries.append({
            'timestamp': entry.action_time,
            'user': entry.user.username,
            'action': action_type,
            'content_type': entry.content_type.model if entry.content_type else 'Unknown',
            'object_id': entry.object_id,
            'object_repr': entry.object_repr,
            'change_message': entry.change_message
        })
    
    # Get summary statistics
    users = User.objects.filter(id__in=log_entries.values_list('user_id', flat=True).distinct())
    user_stats = []
    
    for user in users:
        user_entries = log_entries.filter(user=user)
        additions = user_entries.filter(action_flag=ADDITION).count()
        changes = user_entries.filter(action_flag=CHANGE).count()
        deletions = user_entries.filter(action_flag=DELETION).count()
        
        user_stats.append({
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'additions': additions,
            'changes': changes,
            'deletions': deletions,
            'total_actions': additions + changes + deletions
        })
    
    # Sort by total actions (descending)
    user_stats.sort(key=lambda x: x['total_actions'], reverse=True)
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'user_id': user_id,
        'content_type': content_type,
        'total_entries': log_entries.count(),
        'user_stats': user_stats,
        'entries': formatted_entries
    }

def generate_match_scorecard(match_id):
    """
    Generate a detailed scorecard for a specific match.
    
    Parameters:
    - match_id: ID of the match to generate scorecard for
    
    Returns a dictionary with match details and player performances
    """
    from .models import Match, MatchPlayer
    from django.db.models import Sum
    
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return {'error': 'Match not found'}
    
    # Get all players in this match
    match_players = MatchPlayer.objects.filter(match=match).select_related('player')
    
    # Batting scorecard
    batting_scorecard = []
    for mp in match_players.filter(batting_order__isnull=False).order_by('innings_number', 'batting_order'):
        batting_scorecard.append({
            'player_name': str(mp.player),
            'innings': mp.innings_number,
            'batting_position': mp.batting_order,
            'runs': mp.runs_scored or 0,
            'balls': mp.balls_faced or 0,
            'fours': mp.fours or 0,
            'sixes': mp.sixes or 0,
            'strike_rate': round((mp.runs_scored / mp.balls_faced * 100), 2) if mp.balls_faced and mp.balls_faced > 0 else 0,
            'how_out': mp.how_out or 'not out',
            'bowler': str(mp.bowler) if mp.bowler else '',
            'fielder': str(mp.fielder) if mp.fielder else ''
        })
    
    # Bowling scorecard
    bowling_scorecard = []
    for mp in match_players.filter(overs_bowled__gt=0).order_by('innings_number'):
        bowling_scorecard.append({
            'player_name': str(mp.player),
            'innings': mp.innings_number,
            'overs': mp.overs_bowled or 0,
            'maidens': mp.maidens_bowled or 0,
            'runs': mp.runs_conceded or 0,
            'wickets': mp.wickets_taken or 0,
            'economy': round(mp.runs_conceded / mp.overs_bowled, 2) if mp.overs_bowled and mp.overs_bowled > 0 else 0,
            'wides': mp.wides or 0,
            'no_balls': mp.no_balls or 0
        })
    
    # Fielding highlights
    fielding_highlights = []
    for mp in match_players.filter(catches__gt=0) | match_players.filter(stumpings__gt=0) | match_players.filter(run_outs__gt=0):
        fielding_highlights.append({
            'player_name': str(mp.player),
            'catches': mp.catches or 0,
            'stumpings': mp.stumpings or 0,
            'run_outs': mp.run_outs or 0,
            'direct_hits': mp.direct_hits or 0
        })
    
    # Match summary
    first_innings_total = match.first_innings_total
    second_innings_total = match.second_innings_total
    opponent_first_innings = match.opponent_first_innings
    opponent_second_innings = match.opponent_second_innings
    
    # Extras
    extras = {
        'ananda_extras_byes': match.ananda_extras_byes or 0,
        'ananda_extras_leg_byes': match.ananda_extras_leg_byes or 0,
        'opponent_extras_byes': match.opponent_extras_byes or 0,
        'opponent_extras_leg_byes': match.opponent_extras_leg_byes or 0,
        'ananda_extras_wides': sum(mp.wides or 0 for mp in match_players.filter(innings_number=2)),
        'ananda_extras_no_balls': sum(mp.no_balls or 0 for mp in match_players.filter(innings_number=2)),
        'opponent_extras_wides': sum(mp.wides or 0 for mp in match_players.filter(innings_number=1)),
        'opponent_extras_no_balls': sum(mp.no_balls or 0 for mp in match_players.filter(innings_number=1))
    }
    
    return {
        'match_id': match.id,
        'match_name': match.name or f"{match.team_name or match.college_name} vs {match.opponent}",
        'date': match.match_date,
        'venue': match.venue,
        'format': match.format.name if match.format else 'Unknown',
        'result': match.result,
        'toss': f"{match.toss_winner} won the toss and elected to {match.toss_decision}" if match.toss_winner else 'Unknown',
        'team_name': match.team_name or match.college_name,
        'opponent': match.opponent,
        'first_innings_total': first_innings_total,
        'second_innings_total': second_innings_total,
        'opponent_first_innings': opponent_first_innings,
        'opponent_second_innings': opponent_second_innings,
        'extras': extras,
        'batting_scorecard': batting_scorecard,
        'bowling_scorecard': bowling_scorecard,
        'fielding_highlights': fielding_highlights,
        'man_of_match': str(match.man_of_match) if match.man_of_match else 'Not awarded'
    }

def generate_player_profile(player_id):
    """
    Generate a detailed profile for a specific player.
    
    Parameters:
    - player_id: ID of the player to generate profile for
    
    Returns a dictionary with player details and performance statistics
    """
    from .models import Player, MatchPlayer, Match
    from django.db.models import Sum, Avg, Max, Count, Q
    
    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return {'error': 'Player not found'}
    
    # Basic player info
    player_info = {
        'id': player.id,
        'name': str(player),
        'dob': player.dob,
        'age': player.age_group,
        'batting_style': player.batting_style,
        'bowling_style': player.bowling_style,
        'primary_role': player.get_primary_role_display(),
        'player_class': player.player_class,
        'year_joined': player.year_joined,
        'jersey_number': player.jersey_number
    }
    
    # Get match statistics
    match_players = MatchPlayer.objects.filter(player=player)
    matches_played = match_players.values('match').distinct().count()
    
    # Batting statistics
    batting_stats = match_players.aggregate(
        innings=Count('id', filter=Q(batting_order__isnull=False)),
        runs=Sum('runs_scored', default=0),
        balls=Sum('balls_faced', default=0),
        fours=Sum('fours', default=0),
        sixes=Sum('sixes', default=0),
        highest_score=Max('runs_scored', default=0),
        not_outs=Count('id', filter=Q(batting_order__isnull=False) & Q(how_out__isnull=True))
    )
    
    # Calculate batting average and strike rate
    innings = batting_stats['innings'] or 0
    not_outs = batting_stats['not_outs'] or 0
    runs = batting_stats['runs'] or 0
    balls = batting_stats['balls'] or 0
    
    if innings - not_outs > 0:
        batting_average = runs / (innings - not_outs)
    else:
        batting_average = runs if runs > 0 else 0
    
    if balls > 0:
        strike_rate = (runs / balls) * 100
    else:
        strike_rate = 0
    
    batting_stats['average'] = round(batting_average, 2)
    batting_stats['strike_rate'] = round(strike_rate, 2)
    
    # Count centuries and half-centuries
    batting_stats['centuries'] = match_players.filter(runs_scored__gte=100).count()
    batting_stats['half_centuries'] = match_players.filter(runs_scored__gte=50, runs_scored__lt=100).count()
    
    # Bowling statistics
    bowling_stats = match_players.aggregate(
        innings=Count('id', filter=Q(overs_bowled__gt=0)),
        wickets=Sum('wickets_taken', default=0),
        runs_conceded=Sum('runs_conceded', default=0),
        overs=Sum('overs_bowled', default=0),
        maidens=Sum('maidens_bowled', default=0),
        wides=Sum('wides', default=0),
        no_balls=Sum('no_balls', default=0)
    )
    
    # Calculate bowling average, economy, and strike rate
    wickets = bowling_stats['wickets'] or 0
    runs_conceded = bowling_stats['runs_conceded'] or 0
    overs = bowling_stats['overs'] or 0
    
    if wickets > 0:
        bowling_average = runs_conceded / wickets
    else:
        bowling_average = 0
    
    if overs > 0:
        economy_rate = runs_conceded / overs
    else:
        economy_rate = 0
    
    if wickets > 0:
        strike_rate = (overs * 6) / wickets
    else:
        strike_rate = 0
    
    bowling_stats['average'] = round(bowling_average, 2)
    bowling_stats['economy'] = round(economy_rate, 2)
    bowling_stats['strike_rate'] = round(strike_rate, 2)
    
    # Count 5-wicket hauls
    bowling_stats['five_wicket_hauls'] = match_players.filter(wickets_taken__gte=5).count()
    
    # Fielding statistics
    fielding_stats = match_players.aggregate(
        catches=Sum('catches', default=0),
        stumpings=Sum('stumpings', default=0),
        run_outs=Sum('run_outs', default=0),
        direct_hits=Sum('direct_hits', default=0)
    )
    
    # Recent performances (last 5 matches)
    recent_performances = []
    recent_match_players = match_players.order_by('-match__match_date')[:5]
    
    for mp in recent_match_players:
        match = mp.match
        performance = {
            'match_id': match.id,
            'date': match.match_date,
            'opponent': match.opponent,
            'batting': f"{mp.runs_scored or 0} ({mp.balls_faced or 0})" if mp.batting_order is not None else 'Did not bat',
            'bowling': f"{mp.wickets_taken or 0}/{mp.runs_conceded or 0} ({mp.overs_bowled or 0} overs)" if mp.overs_bowled and mp.overs_bowled > 0 else 'Did not bowl',
            'fielding': f"{mp.catches or 0} catches, {mp.stumpings or 0} stumpings, {mp.run_outs or 0} run outs"
        }
        recent_performances.append(performance)
    
    # Attendance statistics
    from .models import PlayerAttendance
    attendance_stats = PlayerAttendance.objects.filter(player=player).aggregate(
        present=Count('id', filter=Q(status='P')),
        absent=Count('id', filter=Q(status='A')),
        late=Count('id', filter=Q(status='L')),
        excused=Count('id', filter=Q(status='E'))
    )
    
    total_sessions = sum(attendance_stats.values())
    if total_sessions > 0:
        attendance_rate = (attendance_stats['present'] + attendance_stats['late']) / total_sessions * 100
    else:
        attendance_rate = 0
    
    attendance_stats['total_sessions'] = total_sessions
    attendance_stats['attendance_rate'] = round(attendance_rate, 2)
    
    return {
        'player_info': player_info,
        'matches_played': matches_played,
        'batting_stats': batting_stats,
        'bowling_stats': bowling_stats,
        'fielding_stats': fielding_stats,
        'recent_performances': recent_performances,
        'attendance_stats': attendance_stats
    }