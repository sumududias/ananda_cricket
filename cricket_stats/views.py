from rest_framework import viewsets
from django.shortcuts import render
from .reports import generate_attendance_report, get_player_performance_summary
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Max, Avg, Count, F
from django.db.models import Q
from django.views.generic import DetailView, TemplateView
from django.contrib import messages
from .models import Player
from .stats_utils import get_player_stats_context
from .models import Player, Match, Team, Tournament, PlayerAttendance, MatchPlayer, Substitution, MatchFormat, TeamStanding, BattingInnings, BowlingInnings

from .serializers import (
    PlayerSerializer, MatchSerializer, TeamSerializer,
    TournamentSerializer, MatchPlayerSerializer,
    SubstitutionSerializer, TeamStandingSerializer,
    BattingInningsSerializer, BowlingInningsSerializer
)

from django.views.decorators.cache import cache_page

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

class BattingInningsViewSet(viewsets.ModelViewSet):
    queryset = BattingInnings.objects.all()
    serializer_class = BattingInningsSerializer

class BowlingInningsViewSet(viewsets.ModelViewSet):
    queryset = BowlingInnings.objects.all()
    serializer_class = BowlingInningsSerializer

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

@cache_page(60 * 15)  # Cache for 15 minutes
def match_list(request):
    """View for displaying a list of matches."""
    matches = Match.objects.all().order_by('-match_date')
    
    # Filter by year if provided
    year = request.GET.get('year')
    if year:
        try:
            year = int(year)
            matches = matches.filter(match_date__year=year)
        except ValueError:
            pass
    
    # Filter by format if provided
    format_id = request.GET.get('format')
    if format_id:
        try:
            format_id = int(format_id)
            matches = matches.filter(format_id=format_id)
        except ValueError:
            pass
    
    # Get available years and formats for filtering
    years = Match.objects.dates('match_date', 'year', order='DESC')
    formats = MatchFormat.objects.all()
    
    context = {
        'title': 'Matches',
        'matches': matches,
        'years': years,
        'formats': formats,
        'selected_year': year,
        'selected_format': format_id
    }
    
    return render(request, 'cricket_stats/match_list.html', context)

@login_required
def reports_dashboard(request):
    """Dashboard for all reports."""
    return render(request, 'cricket_stats/reports_dashboard.html', {
        'title': 'Reports Dashboard'
    })

@login_required
def attendance_report(request):
    """View for attendance reports."""
    from .models import Player, TrainingSession, PlayerAttendance
    from django.utils import timezone
    from datetime import datetime, timedelta
    from .reports import generate_attendance_report
    
    # Get filter parameters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    age_group = request.GET.get('age_group')
    player_class = request.GET.get('player_class')
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Generate report data for players
    report_data = generate_attendance_report(
        start_date=start_date,
        end_date=end_date,
        age_group=age_group,
        player_class=player_class
    )
    
    # Debug the report data
    print(f"Generated attendance report with {len(report_data)} players")
    for player_id, data in report_data.items():
        print(f"Player {player_id}: {data['name']} - Present: {data['present']}, Absent: {data['absent']}, Excused: {data['excused']}, Late: {data['late']}")
    
    # Get training sessions for the session analysis section
    training_sessions = TrainingSession.objects.all()
    
    # Apply date filters if provided
    if start_date:
        training_sessions = training_sessions.filter(date__gte=start_date)
    if end_date:
        training_sessions = training_sessions.filter(date__lte=end_date)
    
    # Generate session data
    session_data = []
    for session in training_sessions:
        # Get attendance records for this session
        attendance_records = PlayerAttendance.objects.filter(training_session=session)
        
        # Filter by age group and player class if needed
        if age_group or player_class:
            players_query = Player.objects.all()
            if age_group:
                # We need to filter by the property
                player_ids = []
                for player in players_query:
                    if player.age_group == age_group:
                        player_ids.append(player.id)
                players_query = players_query.filter(id__in=player_ids)
            
            if player_class:
                players_query = players_query.filter(player_class=player_class)
            
            attendance_records = attendance_records.filter(player__in=players_query)
        
        # Count by status
        present_count = attendance_records.filter(status='P').count()
        absent_count = attendance_records.filter(status='A').count()
        excused_count = attendance_records.filter(status='E').count()
        late_count = attendance_records.filter(status='L').count()
        
        # Calculate attendance rate
        total_records = present_count + absent_count + excused_count + late_count
        attendance_rate = (present_count + late_count) / total_records * 100 if total_records > 0 else 0
        
        # Add to session data
        session_data.append({
            'date': session.date,
            'session_type': session.get_session_type_display(),
            'present': present_count,
            'absent': absent_count,
            'excused': excused_count,
            'late': late_count,
            'attendance_rate': attendance_rate
        })
    
    # Get available filter options for the form
    age_groups = ['U13', 'U15', 'U17', 'U19']
    player_classes = Player.objects.values_list('player_class', flat=True).distinct()
    
    context = {
        'title': 'Attendance Report',
        'report_data': report_data,
        'session_data': session_data,
        'age_groups': age_groups,
        'player_classes': player_classes,
        'selected_age_group': age_group,
        'selected_player_class': player_class,
        'start_date': start_date,
        'end_date': end_date,
        'print_mode': 'print' in request.GET  # Check if print mode is requested
    }
    
    template = 'cricket_stats/attendance_report_print.html' if 'print' in request.GET else 'cricket_stats/attendance_report.html'
    return render(request, template, context)

@login_required
def audit_report(request):
    """View for displaying audit logs from the admin log."""
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    from django.utils.text import capfirst
    from django.utils.encoding import force_str
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user_id')
    content_type = request.GET.get('content_type')
    
    # Convert date strings to datetime objects if provided
    if start_date:
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            from datetime import datetime, timedelta
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Set to end of day
            end_date = end_date + timedelta(days=1, microseconds=-1)
        except ValueError:
            end_date = None
    
    # Start with all log entries
    log_entries = LogEntry.objects.all().select_related('user', 'content_type').order_by('-action_time')
    
    # Apply filters
    if start_date:
        log_entries = log_entries.filter(action_time__gte=start_date)
    if end_date:
        log_entries = log_entries.filter(action_time__lte=end_date)
    if user_id:
        log_entries = log_entries.filter(user_id=user_id)
    if content_type:
        content_type_id = ContentType.objects.get(model=content_type.lower()).id
        log_entries = log_entries.filter(content_type_id=content_type_id)
    
    # Limit to most recent entries for performance
    log_entries = log_entries[:100]
    
    # Format log entries for display
    audit_logs = []
    for entry in log_entries:
        # Get action description
        if entry.action_flag == 1:
            action = 'Added'
        elif entry.action_flag == 2:
            action = 'Changed'
        elif entry.action_flag == 3:
            action = 'Deleted'
        else:
            action = 'Unknown'
        
        # Format the entry
        audit_logs.append({
            'timestamp': entry.action_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': entry.user.username if entry.user else 'System',
            'action': f"{action} {entry.content_type}",
            'details': f"{entry.object_repr} - {entry.change_message}"
        })
    
    # Get users for filter dropdown
    users = User.objects.all().order_by('username')
    
    # Get content types for filter dropdown
    content_types = ContentType.objects.filter(
        app_label='cricket_stats'
    ).order_by('model')
    
    context = {
        'title': 'System Audit Report',
        'audit_logs': audit_logs,
        'users': users,
        'content_types': content_types,
        'selected_user': user_id,
        'selected_content_type': content_type,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
    }
    
    return render(request, 'cricket_stats/audit_report.html', context)

@cache_page(60 * 15)  # Cache for 15 minutes
def match_scorecard(request, match_id):
    """View for displaying match scorecard."""
    match = get_object_or_404(Match, pk=match_id)
    
    # Debug information
    print(f"Generating scorecard for match ID: {match_id}")
    print(f"Match format: {match.format}")
    
    # Get all players in this match
    match_players = MatchPlayer.objects.filter(match=match).select_related('player')
    
    # Debug count of players
    print(f"Total players in match: {match_players.count()}")
    
    # Get batting data for both innings
    first_innings_batting = match_players.filter(
        innings_number=1, 
        batting_order__isnull=False
    ).order_by('batting_order')
    
    second_innings_batting = match_players.filter(
        innings_number=2, 
        batting_order__isnull=False
    ).order_by('batting_order')
    
    # Get bowling data for both innings
    first_innings_bowling = match_players.filter(
        innings_number=1, 
        overs_bowled__gt=0
    ).order_by('-wickets_taken', 'runs_conceded')
    
    second_innings_bowling = match_players.filter(
        innings_number=2, 
        overs_bowled__gt=0
    ).order_by('-wickets_taken', 'runs_conceded')
    
    # Debug data counts
    print(f"First innings batsmen: {first_innings_batting.count()}")
    print(f"Second innings batsmen: {second_innings_batting.count()}")
    print(f"First innings bowlers: {first_innings_bowling.count()}")
    print(f"Second innings bowlers: {second_innings_bowling.count()}")
    
    # Calculate team totals for each innings
    first_innings_total = {
        'runs': first_innings_batting.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
        'wickets': first_innings_batting.exclude(how_out__isnull=True).count(),
        'overs': first_innings_bowling.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
    }
    
    second_innings_total = {
        'runs': second_innings_batting.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
        'wickets': second_innings_batting.exclude(how_out__isnull=True).count(),
        'overs': second_innings_bowling.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
    }
    
    # Get fielding highlights
    fielding_highlights = match_players.filter(
        Q(catches__gt=0) | Q(stumpings__gt=0) | Q(run_outs__gt=0)
    ).annotate(
        total_dismissals=F('catches') + F('stumpings') + F('run_outs')
    ).order_by('-total_dismissals')
    
    # Determine if this is a multi-day match format
    multi_day_formats = ["Test Match", "2 Day Match", "3 Day Match", "2 Day Practice Match", "3 Day Practice Match", "2 or 3 Day Practice Match"]
    format_name = str(match.format)  # Convert to string to handle any custom __str__ method
    
    # Alternative check for multi-day matches
    is_multi_day = False
    if format_name in multi_day_formats:
        is_multi_day = True
    elif "Day" in format_name and ("Practice" in format_name or "Test" in format_name):
        is_multi_day = True
    
    # Debug format information
    print(f"Format name: {format_name}")
    print(f"Is in multi-day formats: {is_multi_day}")
    
    # Get top scorers for the match and calculate strike rate
    top_scorers = match_players.filter(runs_scored__gt=0).order_by('-runs_scored')[:3]
    
    # Calculate strike rate for each batsman
    for batsman in top_scorers:
        if batsman.balls_faced and batsman.balls_faced > 0:
            batsman.strike_rate = (batsman.runs_scored * 100) / batsman.balls_faced
        else:
            batsman.strike_rate = 0.0
    
    # Get top wicket takers for the match
    top_wicket_takers = match_players.filter(wickets_taken__gt=0).order_by('-wickets_taken')[:3]
    
    # Prepare context for the template
    context = {
        'match': match,
        'first_innings_batting': first_innings_batting,
        'second_innings_batting': second_innings_batting,
        'first_innings_bowling': first_innings_bowling,
        'second_innings_bowling': second_innings_bowling,
        'first_innings_total': first_innings_total,
        'second_innings_total': second_innings_total,
        'fielding_highlights': fielding_highlights,
        'top_scorers': top_scorers,
        'top_wicket_takers': top_wicket_takers,
        'title': f"{match.team_name} vs {match.opponent} - {match.match_date}",
        'is_multi_day_match': is_multi_day,
        'format_name': format_name
    }
    
    # Always use the regular template
    return render(request, 'cricket_stats/match_scorecard.html', context)

def player_profile(request, player_id):
    """Display player profile and statistics."""
    player = get_object_or_404(Player, pk=player_id)
    
    # Get filter parameters
    selected_year = request.GET.get('year')
    
    # Get all match stats for the player
    match_stats = MatchPlayer.objects.filter(player=player, is_playing_xi=True)
    
    # Apply year filter if selected
    if selected_year and selected_year.isdigit():
        year = int(selected_year)
        match_stats = match_stats.filter(match__match_date__year=year)
    
    # Get all available years for the filter
    available_years = MatchPlayer.objects.filter(
        player=player, 
        is_playing_xi=True
    ).values_list(
        'match__match_date__year', flat=True
    ).distinct().order_by('-match__match_date__year')
    
    # Debug info
    print(f"Player: {player.first_name} {player.last_name}")
    print(f"Match stats count: {match_stats.count()}")
    
    # Helper function to calculate stats
    def calculate_stats(match_qs):
        # Debug info
        print(f"\nCalculating stats for query set with {match_qs.count()} matches")
        
        # Calculate batting stats
        batting_stats = {
            'matches': match_qs.values('match').distinct().count(),
            'innings': match_qs.filter(batting_order__isnull=False).count(),
            'runs': match_qs.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
            'balls_faced': match_qs.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0,
            'fours': match_qs.aggregate(Sum('fours'))['fours__sum'] or 0 if match_qs.exists() else 0,
            'sixes': match_qs.aggregate(Sum('sixes'))['sixes__sum'] or 0 if match_qs.exists() else 0,
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
            'maidens': match_qs.aggregate(Sum('maidens_bowled'))['maidens_bowled__sum'] or 0,
            'wides': match_qs.aggregate(Sum('wides'))['wides__sum'] or 0,
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
            'run_outs': match_qs.aggregate(Sum('run_outs'))['run_outs__sum'] or 0,
            'dropped_catches': match_qs.aggregate(Sum('dropped_catches'))['dropped_catches__sum'] or 0,
            'total_dismissals': 0  # Will be calculated below
        }
        fielding_stats['total_dismissals'] = (
            fielding_stats['catches'] + 
            fielding_stats['stumpings'] + 
            fielding_stats['run_outs']
        )
        
        # Debug info
        print("\nFielding stats:")
        print(f"Catches: {fielding_stats['catches']}")
        print(f"Stumpings: {fielding_stats['stumpings']}")
        print(f"Run outs: {fielding_stats['run_outs']}")
        print(f"Dropped catches: {fielding_stats['dropped_catches']}")
        print(f"Total dismissals: {fielding_stats['total_dismissals']}")
        
        return {
            'batting': batting_stats, 
            'bowling': bowling_stats,
            'fielding': fielding_stats
        }
    
    # Get all match formats from the database
    formats = MatchFormat.objects.all()
    print(f"Available formats in database: {[(f.id, f.name) for f in formats]}")
    
    # Calculate overall stats
    overall_stats = calculate_stats(match_stats)
    
    # Initialize context with player and overall stats
    context = {
        'player': player,
        'overall_stats': overall_stats,
        'available_years': available_years,
        'selected_year': selected_year
    }
    
    # Find format IDs for each type
    multi_day_format = formats.filter(is_limited_overs=False, is_practice=False).first()
    limited_overs_format = formats.filter(is_limited_overs=True, is_practice=False).first()
    multi_day_practice_format = formats.filter(is_limited_overs=False, is_practice=True).first()
    limited_overs_practice_format = formats.filter(is_limited_overs=True, is_practice=True).first()
    
    # Debug format IDs
    print(f"Multi-day format: {multi_day_format.id if multi_day_format else 'Not found'}")
    print(f"Limited overs format: {limited_overs_format.id if limited_overs_format else 'Not found'}")
    print(f"Multi-day practice format: {multi_day_practice_format.id if multi_day_practice_format else 'Not found'}")
    print(f"Limited overs practice format: {limited_overs_practice_format.id if limited_overs_practice_format else 'Not found'}")
    
    # Calculate stats for each format type
    if multi_day_format:
        multi_day_stats = match_stats.filter(match__format=multi_day_format)
        context['multi_day_stats'] = calculate_stats(multi_day_stats)
        print(f"Multi-day matches: {multi_day_stats.count()}")
    else:
        context['multi_day_stats'] = calculate_stats(match_stats.filter(pk__in=[]))
    
    if limited_overs_format:
        limited_stats = match_stats.filter(match__format=limited_overs_format)
        context['limited_stats'] = calculate_stats(limited_stats)
        print(f"Limited overs matches: {limited_stats.count()}")
    else:
        context['limited_stats'] = calculate_stats(match_stats.filter(pk__in=[]))
    
    if multi_day_practice_format:
        multi_day_practice_stats = match_stats.filter(match__format=multi_day_practice_format)
        context['multi_day_practice_stats'] = calculate_stats(multi_day_practice_stats)
        print(f"Multi-day practice matches: {multi_day_practice_stats.count()}")
    else:
        context['multi_day_practice_stats'] = calculate_stats(match_stats.filter(pk__in=[]))
    
    if limited_overs_practice_format:
        limited_practice_stats = match_stats.filter(match__format=limited_overs_practice_format)
        context['limited_practice_stats'] = calculate_stats(limited_practice_stats)
        print(f"Limited overs practice matches: {limited_practice_stats.count()}")
    else:
        context['limited_practice_stats'] = calculate_stats(match_stats.filter(pk__in=[]))
    
    return render(request, 'cricket_stats/player_profile.html', context)

@login_required
def player_profile_report(request, player_id):
    """Enhanced player profile view."""
    from .reports import generate_player_profile
    from .models import Player
    
    # Generate player profile data
    profile_data = generate_player_profile(player_id)
    
    # Check if player exists
    if 'error' in profile_data:
        messages.error(request, profile_data['error'])
        return redirect('cricket_stats:players')
    
    context = {
        'title': f"Player Profile: {profile_data['player_info']['name']}",
        'profile': profile_data
    }
    
    # Always use the regular template
    return render(request, 'cricket_stats/player_profile.html', context)

class PlayerDetailView(DetailView):
    model = Player
    template_name = 'cricket_stats/player_detail.html'
    context_object_name = 'player'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.request.GET.get('year')
        format_id = self.request.GET.get('format')
        context.update(get_player_stats_context(self.object, year, format_id))
        return context

class PlayerProfileReport(DetailView):
    model = Player
    template_name = 'cricket_stats/player_profile.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object
        context.update(get_player_stats_context(player))
        return context

# Match innings views for detailed scorecard display
class MatchFirstInningsView(DetailView):
    """View for displaying first innings details of a match"""
    model = Match
    template_name = 'cricket_stats/match_first_innings.html'
    context_object_name = 'match'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object
        
        # Get batting scorecard for first innings
        batting_scorecard = MatchPlayer.objects.filter(
            match=match,
            innings_number=1,
            batting_order__isnull=False
        ).order_by('batting_order').select_related('player', 'bowler', 'fielder')
        
        # Get bowling figures for first innings
        bowling_figures = MatchPlayer.objects.filter(
            match=match,
            innings_number=1,
            overs_bowled__gt=0
        ).order_by('-wickets_taken', 'runs_conceded').select_related('player')
        
        context.update({
            'batting_scorecard': batting_scorecard,
            'bowling_figures': bowling_figures,
            'innings_number': 1,
            'innings_total': match.first_innings_total,
            'extras': {
                'wides': sum(mp.wides or 0 for mp in bowling_figures),
                'no_balls': sum(mp.no_balls or 0 for mp in bowling_figures),
                'byes': match.ananda_extras_byes or 0,
                'leg_byes': match.ananda_extras_leg_byes or 0
            }
        })
        return context

class MatchSecondInningsView(DetailView):
    """View for displaying second innings details of a match"""
    model = Match
    template_name = 'cricket_stats/match_second_innings.html'
    context_object_name = 'match'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object
        
        # Get batting scorecard for second innings
        batting_scorecard = MatchPlayer.objects.filter(
            match=match,
            innings_number=2,
            batting_order__isnull=False
        ).order_by('batting_order').select_related('player', 'bowler', 'fielder')
        
        # Get bowling figures for second innings
        bowling_figures = MatchPlayer.objects.filter(
            match=match,
            innings_number=2,
            overs_bowled__gt=0
        ).order_by('-wickets_taken', 'runs_conceded').select_related('player')
        
        context.update({
            'batting_scorecard': batting_scorecard,
            'bowling_figures': bowling_figures,
            'innings_number': 2,
            'innings_total': match.second_innings_total,
            'extras': {
                'wides': sum(mp.wides or 0 for mp in bowling_figures),
                'no_balls': sum(mp.no_balls or 0 for mp in bowling_figures),
                'byes': match.opponent_extras_byes or 0,
                'leg_byes': match.opponent_extras_leg_byes or 0
            }
        })
        return context

class MatchTotalsView(DetailView):
    """View for displaying match summary and totals"""
    model = Match
    template_name = 'cricket_stats/match_totals.html'
    context_object_name = 'match'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object
        
        # Get player of the match and other notable performances
        notable_performances = []
        
        # Add man of the match
        if match.man_of_match:
            mom_performance = MatchPlayer.objects.filter(match=match, player=match.man_of_match).first()
            if mom_performance:
                notable_performances.append({
                    'player': match.man_of_match,
                    'performance': f"{mom_performance.runs_scored or 0} runs & {mom_performance.wickets_taken or 0} wickets",
                    'type': 'Man of the Match'
                })
        
        # Add top scorer
        top_scorer = MatchPlayer.objects.filter(match=match).order_by('-runs_scored').first()
        if top_scorer and top_scorer.runs_scored > 0:
            notable_performances.append({
                'player': top_scorer.player,
                'performance': f"{top_scorer.runs_scored} runs ({top_scorer.balls_faced or 0} balls)",
                'type': 'Top Scorer'
            })
        
        # Add top wicket taker
        top_bowler = MatchPlayer.objects.filter(match=match).order_by('-wickets_taken').first()
        if top_bowler and top_bowler.wickets_taken > 0:
            notable_performances.append({
                'player': top_bowler.player,
                'performance': f"{top_bowler.wickets_taken}-{top_bowler.runs_conceded} ({top_bowler.overs_bowled} overs)",
                'type': 'Top Bowler'
            })
        
        context.update({
            'notable_performances': notable_performances,
            'first_innings_total': match.first_innings_total,
            'second_innings_total': match.second_innings_total,
            'opponent_first_innings': match.opponent_first_innings,
            'opponent_second_innings': match.opponent_second_innings,
            'result': match.result
        })
        return context

@login_required
def team_performance_report(request):
    """View for team performance report."""
    from django.db.models import Count, Sum, Avg, F, Q, ExpressionWrapper, FloatField
    from django.db.models.functions import ExtractYear
    
    # Get filter parameters
    year = request.GET.get('year')
    format_id = request.GET.get('format')
    
    # Start with all matches
    matches = Match.objects.all()
    
    # Apply filters
    if year:
        matches = matches.filter(match_date__year=year)
    if format_id:
        matches = matches.filter(format_id=format_id)
    
    # Get match statistics
    match_stats = matches.aggregate(
        total_matches=Count('id'),
        matches_won=Count('id', filter=Q(result__icontains='won')),
        matches_lost=Count('id', filter=Q(result__icontains='lost')),
        matches_drawn=Count('id', filter=Q(result__icontains='draw')),
        matches_tied=Count('id', filter=Q(result__icontains='tie')),
        matches_no_result=Count('id', filter=Q(result__icontains='no result') | Q(result__isnull=True))
    )
    
    # Calculate win percentage
    if match_stats['total_matches'] > 0:
        match_stats['win_percentage'] = (match_stats['matches_won'] / match_stats['total_matches']) * 100
    else:
        match_stats['win_percentage'] = 0
    
    # Get batting statistics
    batting_stats = MatchPlayer.objects.filter(match__in=matches).aggregate(
        total_runs=Sum('runs_scored'),
        total_balls=Sum('balls_faced'),
        total_fours=Sum('fours'),
        total_sixes=Sum('sixes'),
        total_centuries=Count('id', filter=Q(runs_scored__gte=100)),
        total_fifties=Count('id', filter=Q(runs_scored__gte=50, runs_scored__lt=100))
    )
    
    # Calculate batting strike rate
    if batting_stats['total_balls'] and batting_stats['total_balls'] > 0:
        batting_stats['strike_rate'] = (batting_stats['total_runs'] / batting_stats['total_balls']) * 100
    else:
        batting_stats['strike_rate'] = 0
    
    # Get bowling statistics
    bowling_stats = MatchPlayer.objects.filter(match__in=matches).aggregate(
        total_wickets=Sum('wickets_taken'),
        total_runs_conceded=Sum('runs_conceded'),
        total_overs=Sum('overs_bowled'),
        total_maidens=Sum('maidens_bowled'),
        total_five_wickets=Count('id', filter=Q(wickets_taken__gte=5))
    )
    
    # Calculate bowling economy
    if bowling_stats['total_overs'] and bowling_stats['total_overs'] > 0:
        bowling_stats['economy'] = bowling_stats['total_runs_conceded'] / bowling_stats['total_overs']
    else:
        bowling_stats['economy'] = 0
    
    # Get top performers
    top_batsmen = MatchPlayer.objects.filter(match__in=matches).values(
        'player__id', 'player__first_name', 'player__last_name'
    ).annotate(
        total_runs=Sum('runs_scored')
    ).order_by('-total_runs')[:5]
    
    top_bowlers = MatchPlayer.objects.filter(match__in=matches).values(
        'player__id', 'player__first_name', 'player__last_name'
    ).annotate(
        total_wickets=Sum('wickets_taken')
    ).order_by('-total_wickets')[:5]
    
    # Get available years for filter
    years = Match.objects.dates('match_date', 'year').values_list('match_date__year', flat=True)
    
    # Get available formats for filter
    formats = MatchFormat.objects.all()
    
    context = {
        'title': 'Team Performance Report',
        'match_stats': match_stats,
        'batting_stats': batting_stats,
        'bowling_stats': bowling_stats,
        'top_batsmen': top_batsmen,
        'top_bowlers': top_bowlers,
        'years': years,
        'formats': formats,
        'selected_year': year,
        'selected_format': format_id,
        'print_mode': 'print' in request.GET
    }
    
    template = 'cricket_stats/team_performance_report_print.html' if 'print' in request.GET else 'cricket_stats/team_performance_report.html'
    return render(request, template, context)

@login_required
def season_summary_report(request):
    """View for season summary report."""
    from django.db.models import Count, Sum, Avg, F, Q, ExpressionWrapper, FloatField
    from django.db.models.functions import ExtractYear
    
    # Get filter parameters
    year = request.GET.get('year')
    
    # Default to current year if not specified
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    # Get all matches for the selected year
    matches = Match.objects.filter(match_date__year=year)
    
    # Get match statistics by format
    format_stats = []
    for match_format in MatchFormat.objects.all():
        format_matches = matches.filter(format=match_format)
        
        if format_matches.exists():
            stats = {
                'format': match_format.name,
                'total_matches': format_matches.count(),
                'matches_won': format_matches.filter(result__icontains='won').count(),
                'matches_lost': format_matches.filter(result__icontains='lost').count(),
                'matches_drawn': format_matches.filter(result__icontains='draw').count(),
            }
            
            # Calculate win percentage
            if stats['total_matches'] > 0:
                stats['win_percentage'] = (stats['matches_won'] / stats['total_matches']) * 100
            else:
                stats['win_percentage'] = 0
                
            format_stats.append(stats)
    
    # Get monthly performance
    monthly_stats = []
    for month in range(1, 13):
        month_matches = matches.filter(match_date__month=month)
        
        if month_matches.exists():
            stats = {
                'month': month,
                'month_name': {
                    1: 'January', 2: 'February', 3: 'March', 4: 'April',
                    5: 'May', 6: 'June', 7: 'July', 8: 'August',
                    9: 'September', 10: 'October', 11: 'November', 12: 'December'
                }[month],
                'total_matches': month_matches.count(),
                'matches_won': month_matches.filter(result__icontains='won').count(),
                'matches_lost': month_matches.filter(result__icontains='lost').count(),
                'matches_drawn': month_matches.filter(result__icontains='draw').count(),
            }
            
            # Calculate win percentage
            if stats['total_matches'] > 0:
                stats['win_percentage'] = (stats['matches_won'] / stats['total_matches']) * 100
            else:
                stats['win_percentage'] = 0
                
            monthly_stats.append(stats)
    
    # Get top performers for the season
    top_batsmen = MatchPlayer.objects.filter(match__in=matches).values(
        'player__id', 'player__first_name', 'player__last_name'
    ).annotate(
        total_runs=Sum('runs_scored'),
        matches_played=Count('match', distinct=True),
        innings=Count('id', filter=Q(batting_order__isnull=False)),
        average=ExpressionWrapper(
            Sum('runs_scored') * 1.0 / (Count('id', filter=Q(batting_order__isnull=False)) - 
                                        Count('id', filter=Q(how_out='') | Q(how_out__isnull=True))),
            output_field=FloatField()
        )
    ).filter(total_runs__gt=0).order_by('-total_runs')[:10]
    
    top_bowlers = MatchPlayer.objects.filter(match__in=matches).values(
        'player__id', 'player__first_name', 'player__last_name'
    ).annotate(
        total_wickets=Sum('wickets_taken'),
        matches_played=Count('match', distinct=True),
        innings=Count('id', filter=Q(overs_bowled__gt=0)),
        economy=ExpressionWrapper(
            Sum('runs_conceded') * 1.0 / Sum('overs_bowled'),
            output_field=FloatField()
        )
    ).filter(total_wickets__gt=0).order_by('-total_wickets')[:10]
    
    # Get available years for filter
    years = Match.objects.dates('match_date', 'year').values_list('match_date__year', flat=True)
    
    context = {
        'title': f'Season Summary Report - {year}',
        'format_stats': format_stats,
        'monthly_stats': monthly_stats,
        'top_batsmen': top_batsmen,
        'top_bowlers': top_bowlers,
        'years': years,
        'selected_year': year,
        'print_mode': 'print' in request.GET
    }
    
    template = 'cricket_stats/season_summary_report_print.html' if 'print' in request.GET else 'cricket_stats/season_summary_report.html'
    return render(request, template, context)

@login_required
def batch_attendance_entry(request, session_id=None):
    """View for batch entry of player attendance for a training session."""
    from .models import Player, TrainingSession, PlayerAttendance
    
    # Get the training session or redirect to create a new one
    if session_id:
        training_session = get_object_or_404(TrainingSession, pk=session_id)
    else:
        return redirect('cricket_stats:training_session_list')
    
    # Get all active players
    active_players = Player.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    # Check if this is a form submission
    if request.method == 'POST':
        # Process the form data
        for player in active_players:
            player_key = f'player_{player.id}'
            status_key = f'status_{player.id}'
            
            if player_key in request.POST and status_key in request.POST:
                status = request.POST.get(status_key)
                
                # Create or update attendance record
                attendance, created = PlayerAttendance.objects.update_or_create(
                    player=player,
                    training_session=training_session,
                    defaults={
                        'status': status,
                        'reported_by': request.user,
                    }
                )
        
        messages.success(request, f'Attendance for {training_session} has been recorded successfully.')
        return redirect('cricket_stats:training_session_list')
    
    # Check for existing attendance records
    existing_attendance = {}
    for attendance in PlayerAttendance.objects.filter(training_session=training_session):
        existing_attendance[attendance.player_id] = attendance.status
    
    context = {
        'training_session': training_session,
        'active_players': active_players,
        'existing_attendance': existing_attendance,
        'attendance_choices': PlayerAttendance.ATTENDANCE_CHOICES,
    }
    
    # Check if print mode is requested
    if 'print' in request.GET:
        return render(request, 'cricket_stats/batch_attendance_entry_print.html', context)
    
    return render(request, 'cricket_stats/batch_attendance_entry.html', context)

@login_required
def training_session_list(request):
    """View to list all training sessions."""
    from .models import TrainingSession
    from django.core.paginator import Paginator
    from datetime import datetime, timedelta
    
    # Get filter parameters
    date_filter = request.GET.get('date_filter', 'recent')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    queryset = TrainingSession.objects.all()
    
    # Apply date filter
    if date_filter == 'recent':
        # Show sessions from the last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        queryset = queryset.filter(date__gte=thirty_days_ago)
    elif date_filter == 'upcoming':
        # Show upcoming sessions
        today = datetime.now().date()
        queryset = queryset.filter(date__gte=today)
    elif date_filter == 'past':
        # Show past sessions
        today = datetime.now().date()
        queryset = queryset.filter(date__lt=today)
    
    # Apply search if provided
    if search_query:
        queryset = queryset.filter(notes__icontains=search_query)
    
    # Order by date and time
    queryset = queryset.order_by('-date', '-start_time')
    
    # Paginate the results - 20 items per page
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    training_sessions = paginator.get_page(page_number)
    
    context = {
        'training_sessions': training_sessions,
        'date_filter': date_filter,
        'search_query': search_query,
        'page_obj': training_sessions,  # For pagination template
    }
    
    return render(request, 'cricket_stats/training_session_list.html', context)