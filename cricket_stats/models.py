from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Q, Max
from django.core.exceptions import ValidationError
import logging
from .models_choices import (
    BOWLING_STYLE_CHOICES, BATTING_STYLE_CHOICES, PLAYER_CLASS_CHOICES,
    VENUE_CHOICES, MATCH_RESULT_CHOICES, DISMISSAL_TYPE_CHOICES
)

logger = logging.getLogger(__name__)

class MatchFormat(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10, unique=True)
    is_limited_overs = models.BooleanField(default=False)
    is_practice = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Player(models.Model):
    ROLES = (
        ('BAT', 'Batsman'),
        ('BOWL', 'Bowler'),
        ('AR', 'All-Rounder'),
        ('WK', 'Wicket Keeper'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    photo = models.ImageField(upload_to='player_photos/', null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True, help_text="Player's jersey number", db_column='player_jersey_number')
    batting_style = models.CharField(max_length=20, choices=BATTING_STYLE_CHOICES)
    bowling_style = models.CharField(max_length=50, choices=BOWLING_STYLE_CHOICES, blank=True, null=True)
    primary_role = models.CharField(max_length=4, choices=ROLES)
    player_class = models.CharField(max_length=20, choices=PLAYER_CLASS_CHOICES)
    year_joined = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def date_of_birth(self):
        return self.dob

    @property
    def age_group(self):
        from datetime import date
        today = date.today()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        
        if age <= 13:
            return 'U13'
        elif age <= 15:
            return 'U15'
        elif age <= 17:
            return 'U17'
        elif age <= 19:
            return 'U19'
        else:
            return None

    @property
    def get_age_group_display(self):
        age_groups = {
            'U13': 'Under 13',
            'U15': 'Under 15',
            'U17': 'Under 17',
            'U19': 'Under 19'
        }
        return age_groups.get(self.age_group, '')

    @property
    def total_matches(self):
        return self.matchplayer_set.filter(is_playing_xi=True).count()

    @property
    def get_batting_stats(self, year=None, format_id=None):
        queryset = MatchPlayer.objects.filter(player=self)
        if year:
            queryset = queryset.filter(match__match_date__year=year)
        if format_id:
            queryset = queryset.filter(match__format_id=format_id)
        
        stats = queryset.aggregate(
            total_runs=Sum('runs_scored'),
            total_balls=Sum('balls_faced'),
            total_4s=Sum('fours'),
            total_6s=Sum('sixes'),
            total_outs=Count('id', filter=Q(dismissal_type__isnull=False)),
            total_innings=Count('id', filter=Q(did_bat=True)),
            highest_score=Max('runs_scored')
        )
        
        # Calculate batting average and strike rate
        stats['batting_avg'] = round(stats['total_runs'] / stats['total_outs'], 2) if stats['total_outs'] > 0 else 0
        stats['strike_rate'] = round((stats['total_runs'] / stats['total_balls']) * 100, 2) if stats['total_balls'] and stats['total_balls'] > 0 else 0
        
        return stats

    def get_bowling_stats(self, year=None, format_id=None):
        queryset = MatchPlayer.objects.filter(player=self)
        if year:
            queryset = queryset.filter(match__match_date__year=year)
        if format_id:
            queryset = queryset.filter(match__format_id=format_id)
            
        stats = queryset.aggregate(
            total_overs=Sum('overs_bowled'),
            total_maidens=Sum('maidens_bowled'),
            total_runs_conceded=Sum('runs_conceded'),
            total_wickets=Sum('wickets_taken'),
            total_4w=Count('id', filter=Q(wickets_taken=4)),
            total_5w=Count('id', filter=Q(wickets_taken__gte=5))
        )
        
        # Calculate bowling average, economy, and strike rate
        stats['bowling_avg'] = round(stats['total_runs_conceded'] / stats['total_wickets'], 2) if stats['total_wickets'] > 0 else 0
        stats['economy'] = round(stats['total_runs_conceded'] / stats['total_overs'], 2) if stats['total_overs'] > 0 else 0
        stats['strike_rate'] = round((stats['total_overs'] * 6) / stats['total_wickets'], 2) if stats['total_wickets'] > 0 else 0
        
        return stats

    def get_fielding_stats(self, year=None, format_id=None):
        queryset = MatchPlayer.objects.filter(player=self)
        if year:
            queryset = queryset.filter(match__match_date__year=year)
        if format_id:
            queryset = queryset.filter(match__format_id=format_id)
            
        stats = queryset.aggregate(
            total_catches=Sum('catches'),
            total_stumpings=Sum('stumpings'),
            total_run_outs=Sum('run_outs'),
            total_dropped=Sum('missed_catches')
        )
        return stats

    def get_formats(self):
        """Get all formats this player has played in"""
        from django.db.models import Count
        return MatchFormat.objects.filter(
            matches__players=self
        ).annotate(
            matches_played=Count('matches')
        ).order_by('name')

class Team(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20)
    coach = models.CharField(max_length=100)
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='captain_of')

    def __str__(self):
        return f"{self.name} ({self.season})"

class Match(models.Model):
    college_name = models.CharField(max_length=100, default='Ananda College')
    name = models.CharField(max_length=100, blank=True, default='')  # Make name optional with default empty string
    team_name = models.CharField(max_length=100, blank=True, default='')  # Add this line
    team = models.ForeignKey('Team', on_delete=models.PROTECT, related_name='matches', null=True, blank=True)
    opponent = models.CharField(max_length=100)
    match_date = models.DateField()
    venue = models.CharField(max_length=100, choices=VENUE_CHOICES, blank=True, null=True)
    format = models.ForeignKey(MatchFormat, on_delete=models.PROTECT, related_name='matches')
    match_days = models.PositiveSmallIntegerField(
        default=3,
        help_text="Number of days for the match (2 or 3 for multi-day matches)"
    )
    toss_winner = models.CharField(max_length=100, null=True, blank=True)
    toss_decision = models.CharField(max_length=10, null=True, blank=True)
    result = models.CharField(max_length=100, choices=MATCH_RESULT_CHOICES, blank=True, null=True)  # Make name optional with default empty string
    tournament = models.ForeignKey('Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    man_of_match = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='man_of_match_matches')
    
    # Add extras fields
    ananda_extras_byes = models.IntegerField(default=0)
    ananda_extras_leg_byes = models.IntegerField(default=0)
    opponent_extras_byes = models.IntegerField(default=0)
    opponent_extras_leg_byes = models.IntegerField(default=0)
    match_type = models.CharField(max_length=20, default='League')
    
    # Add innings totals
    first_innings_total = models.IntegerField(default=0)
    second_innings_total = models.IntegerField(default=0)
    opponent_first_innings = models.IntegerField(default=0)
    opponent_second_innings = models.IntegerField(default=0)  # Fixed typo here
    
    def get_batting_stats(self):  # Now properly separated
        from .models import MatchPlayer
        stats = MatchPlayer.objects.filter(player=self).aggregate(
            matches=Count('match', distinct=True),
            innings=Count('id', filter=Q(batting_order__isnull=False)),
            not_outs=Count('id', filter=Q(batting_order__isnull=False, how_out__isnull=True)),
            runs=Sum('runs_scored', default=0),
            balls_faced=Sum('balls_faced', default=0),
            fours=Sum('fours', default=0),
            sixes=Sum('sixes', default=0),
            highest_score=models.Max('runs_scored', default=0)
        )

        # Calculate batting average and strike rate
        total_innings = stats['innings'] or 0
        total_not_outs = stats['not_outs'] or 0
        total_runs = stats['runs'] or 0
        total_balls = stats['balls_faced'] or 0
        
        if total_innings - total_not_outs > 0:
            stats['average'] = float(total_runs) / (total_innings - total_not_outs)
        else:
            stats['average'] = 0.0

        if total_balls > 0:
            stats['strike_rate'] = (float(total_runs) / total_balls) * 100
        else:
            stats['strike_rate'] = 0.0

        return stats
    

    def get_bowling_stats(self):
        from .models import MatchPlayer
        stats = MatchPlayer.objects.filter(player=self).aggregate(
            matches=Count('match', distinct=True),
            innings=Count('id', filter=Q(overs_bowled__gt=0)),
            overs=Sum('overs_bowled', default=0),
            runs=Sum('runs_conceded', default=0),
            wickets=Sum('wickets_taken', default=0),
        )

        total_wickets = stats['wickets'] or 0
        total_runs = stats['runs'] or 0
        total_overs = stats['overs'] or 0
        
        # Calculate bowling average
        if total_wickets > 0:
            stats['average'] = float(total_runs) / total_wickets
        else:
            stats['average'] = 0.0

        # Calculate economy rate
        if total_overs > 0:
            stats['economy'] = float(total_runs) / float(total_overs)
        else:
            stats['economy'] = 0.0

        # Calculate strike rate
        if total_wickets > 0:
            stats['strike_rate'] = (float(total_overs * 6) / float(total_wickets))
        else:
            stats['strike_rate'] = 0.0

        # Get best bowling figures
        best_bowling = MatchPlayer.objects.filter(
            player=self,
            wickets_taken__gt=0
        ).order_by('-wickets_taken', 'runs_conceded').first()

        if best_bowling:
            stats['best_bowling'] = f"{best_bowling.wickets_taken}/{best_bowling.runs_conceded}"
        else:
            stats['best_bowling'] = "0/0"

        return stats

    def get_fielding_stats(self):
        from .models import MatchPlayer
        stats = MatchPlayer.objects.filter(player=self).aggregate(
            matches=Count('match', distinct=True),
            catches=Sum('catches', default=0),
            stumpings=Sum('stumpings', default=0),
            runouts=Sum('runouts', default=0)
        )
        return stats

    def get_format_stats(self, format_type):
        """Get player statistics for a specific format (T20/ODI/TEST)"""
        try:
            matches = MatchPlayer.objects.filter(
                match__match_format=format_type,
                player=self,
                is_playing_xi=True
            )
            
            # Calculate batting statistics
            batting_stats = matches.aggregate(
                total_matches=Count('match', distinct=True),
                total_runs=Sum('runs_scored'),
                total_balls=Sum('balls_faced'),
                total_fours=Sum('fours'),
                total_sixes=Sum('sixes'),
                centuries=Count('id', filter=Q(is_century=True)),
                half_centuries=Count('id', filter=Q(is_half_century=True)),
                highest_score=Max('runs_scored'),
                not_outs=Count('id', filter=Q(how_out='Not Out') | Q(how_out__isnull=True))
            )
            
            # Calculate bowling statistics
            bowling_stats = matches.aggregate(
                total_overs=Sum('overs_bowled'),
                total_runs_conceded=Sum('runs_conceded'),
                total_wickets=Sum('wickets_taken'),
                total_maidens=Sum('maidens'),
                total_wides=Sum('wide_balls'),
                total_no_balls=Sum('no_balls')
            )
            
            # Calculate fielding statistics
            fielding_stats = matches.aggregate(
                total_catches=Sum('catches'),
                total_stumpings=Sum('stumpings'),
                total_runouts=Sum('runouts')
            )
            
            # Get total matches and innings
            total_matches = batting_stats['total_matches'] or 0
            total_runs = batting_stats['total_runs'] or 0
            total_balls = batting_stats['total_balls'] or 0
            not_outs = batting_stats['not_outs'] or 0
            
            # Calculate batting averages and strike rates
            if total_balls > 0:
                strike_rate = (total_runs * 100.0) / total_balls
            else:
                strike_rate = 0.0
                
            if total_matches - not_outs > 0:
                batting_average = total_runs / (total_matches - not_outs)
            else:
                batting_average = total_runs if total_runs > 0 else 0.0
            
            # Calculate bowling averages and economy
            total_wickets = bowling_stats['total_wickets'] or 0
            total_runs_conceded = bowling_stats['total_runs_conceded'] or 0
            total_overs = bowling_stats['total_overs'] or 0
            
            if total_wickets > 0:
                bowling_average = total_runs_conceded / total_wickets
            else:
                bowling_average = 0.0
                
            if total_overs > 0:
                economy_rate = float(total_runs_conceded) / float(total_overs)
            else:
                economy_rate = 0.0
            
            return {
                'format': format_type,
                'matches': total_matches,
                'batting': {
                    'runs': total_runs,
                    'balls': total_balls,
                    'average': round(batting_average, 2),
                    'strike_rate': round(strike_rate, 2),
                    'highest_score': batting_stats['highest_score'] or 0,
                    'centuries': batting_stats['centuries'] or 0,
                    'half_centuries': batting_stats['half_centuries'] or 0,
                    'fours': batting_stats['total_fours'] or 0,
                    'sixes': batting_stats['total_sixes'] or 0
                },
                'bowling': {
                    'overs': total_overs,
                    'runs_conceded': total_runs_conceded,
                    'wickets': total_wickets,
                    'average': round(bowling_average, 2),
                    'economy': round(economy_rate, 2),
                    'maidens': bowling_stats['total_maidens'] or 0,
                    'wides': bowling_stats['total_wides'] or 0,
                    'no_balls': bowling_stats['total_no_balls'] or 0
                },
                'fielding': {
                    'catches': fielding_stats['total_catches'] or 0,
                    'stumpings': fielding_stats['total_stumpings'] or 0,
                    'runouts': fielding_stats['total_runouts'] or 0
                }
            }
        except Exception as e:
            print(f"Error calculating stats for {self}: {str(e)}")
            return None
            
    def __str__(self):
        try:
            # First try to use team.name if team is available and valid
            if self.team and hasattr(self.team, 'name'):
                team_name = self.team.name
            # Otherwise fall back to team_name field if it's not empty
            elif self.team_name:
                team_name = self.team_name
            # Finally use college_name as the last resort
            else:
                team_name = self.college_name
        except (ValueError, AttributeError, TypeError):
            # If any error occurs when accessing team, use alternative fields
            if hasattr(self, 'team_name') and self.team_name:
                team_name = self.team_name
            elif hasattr(self, 'college_name') and self.college_name:
                team_name = self.college_name
            else:
                team_name = "Unknown Team"
        
        return f"{team_name} vs {self.opponent} - {self.match_date}"

    @property
    def test_stats(self):
        return self.get_format_stats('TEST')
        
    @property
    def odi_stats(self):
        return self.get_format_stats('ODI')
        
    @property
    def t20_stats(self):
        return self.get_format_stats('T20')

    def get_format_specific_stats(self, match_format):
        matches = MatchPlayer.objects.filter(
            player=self,
            match__match_format=match_format
        )
        
        total_runs = sum(m.runs_scored for m in matches)
        total_wickets = sum(m.wickets_taken for m in matches)
        matches_played = matches.count()
        
        if matches_played > 0:
            batting_average = total_runs / matches_played
            bowling_average = total_runs / total_wickets if total_wickets > 0 else 0
        else:
            batting_average = bowling_average = 0
            
        return {
            'matches': matches_played,
            'runs_innings': models.IntegerField(default=0)
        }

    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['-match_date']

    def clean(self):
        # Remove format validation since it's now a ForeignKey
        pass

    def save(self, *args, **kwargs):
        # First save the instance to get a primary key
        super().save(*args, **kwargs)
        
        # Now calculate and save totals
        self.calculate_totals()
        # Use update_fields to prevent recursion
        super().save(update_fields=['first_innings_total', 'second_innings_total'])

    def calculate_totals(self):
        """Calculate and update match totals"""
        try:
            first_innings = self.matchplayer_set.filter(innings_number=1)
            self.first_innings_total = sum(p.runs_scored or 0 for p in first_innings)
            
            # For limited overs matches (T20/ODI), we only have one innings
            if hasattr(self, 'format') and self.format and not self.format.is_limited_overs:
                second_innings = self.matchplayer_set.filter(innings_number=2)
                self.second_innings_total = sum(p.runs_scored or 0 for p in second_innings)
            else:
                self.second_innings_total = 0
                self.opponent_second_innings = 0
        except Exception as e:
            logger.error(f"Error calculating match totals: {str(e)}")
            raise

class MatchPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    innings_number = models.IntegerField(default=1)
    batting_order = models.IntegerField(null=True, blank=True)
    runs_scored = models.IntegerField(null=True, blank=True)
    balls_faced = models.IntegerField(null=True, blank=True)
    fours = models.IntegerField(null=True, blank=True)
    sixes = models.IntegerField(null=True, blank=True)
    how_out = models.CharField(max_length=100, choices=DISMISSAL_TYPE_CHOICES, blank=True, null=True)
    bowler = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='bowled_players')
    fielder = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='fielded_players')
    overs_bowled = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    maidens_bowled = models.IntegerField(null=True, blank=True)
    runs_conceded = models.IntegerField(null=True, blank=True)
    wickets_taken = models.IntegerField(null=True, blank=True)
    wides = models.IntegerField(null=True, blank=True)
    no_balls = models.IntegerField(null=True, blank=True)
    is_playing_xi = models.BooleanField(default=False)
    is_captain = models.BooleanField(default=False)
    is_keeper = models.BooleanField(default=False)
    
    # Fielding stats
    catches = models.PositiveSmallIntegerField(default=0, help_text='Number of catches taken')
    run_outs = models.PositiveSmallIntegerField(default=0, help_text='Number of run outs effected')
    stumpings = models.PositiveSmallIntegerField(default=0, help_text='Number of stumpings (for wicket-keepers)')
    direct_hits = models.PositiveSmallIntegerField(default=0, help_text='Number of direct hit run outs')
    dropped_catches = models.PositiveSmallIntegerField(default=0, help_text='Number of catches dropped')
    
    # Comments about player selection or performance
    comments = models.TextField(blank=True, null=True, help_text='Comments about player selection or performance')
    
    class Meta:
        ordering = ['match', 'innings_number', 'batting_order']
        unique_together = ('match', 'player', 'innings_number')
    
    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name} - {self.match}"

class TrainingSession(models.Model):
    SESSION_TYPES = [
        ('fitness', 'Fitness Training'),
        ('cricket', 'Cricket Training'),
    ]
    
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_session_type_display()} - {self.date} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

class PlayerAttendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('E', 'Excused'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendance')
    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendance', null=True, blank=True)
    status = models.CharField(max_length=1, choices=ATTENDANCE_CHOICES, default='P')
    notes = models.TextField(blank=True, null=True)
    arrival_time = models.TimeField(null=True, blank=True, help_text="Time player arrived at training")
    departure_time = models.TimeField(null=True, blank=True, help_text="Time player left training")
    time_reported = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Player Attendance'
        unique_together = ('player', 'training_session')
        ordering = ['training_session__date', 'player__first_name']
    
    def __str__(self):
        session_info = str(self.training_session) if self.training_session else "No Session"
        return f"{self.player.first_name} {self.player.last_name} - {session_info} - {self.get_status_display()}"

def get_attendance_stats(self):
    from django.db.models import Count, Q
    total_matches = Match.objects.count()
    attendance = self.attendance.all()
    present = attendance.filter(status='P').count()
    absent = attendance.filter(status='A').count()
    late = attendance.filter(status='L').count()
    excused = attendance.filter(status='E').count()
    
    return {
        'total_matches': total_matches,
        'present': present,
        'absent': absent,
        'late': late,
        'excused': excused,
        'attendance_percentage': (present / total_matches * 100) if total_matches > 0 else 0
    }

class TeamStanding(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    matches_played = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    matches_lost = models.IntegerField(default=0)
    matches_drawn = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    net_run_rate = models.FloatField(default=0.0)
    position = models.IntegerField()

    def __str__(self):
        return f"{self.team} in {self.tournament}"

class BattingInnings(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    innings_number = models.IntegerField(default=1)
    batting_position = models.IntegerField()
    runs_scored = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    how_out = models.CharField(max_length=100, choices=DISMISSAL_TYPE_CHOICES, blank=True, null=True)
    bowler = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='wickets_taken_set')
    fielder = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='catches_taken_set')

    def __str__(self):
        return f"{self.player} - {self.runs_scored}({self.balls_faced}) in {self.match}"

    class Meta:
        unique_together = ('match', 'player', 'innings_number')
        ordering = ['innings_number', 'batting_position']

class BowlingInnings(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    innings_number = models.IntegerField(default=1)
    overs = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    maidens = models.IntegerField(default=0)
    runs_conceded = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    wides = models.IntegerField(default=0)
    no_balls = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.overs}({self.maidens}) in {self.match}"

    class Meta:
        unique_together = ('match', 'player', 'innings_number')
        ordering = ['innings_number']

class Substitution(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_out = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substituted_out')
    player_in = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='substituted_in')
    reason = models.CharField(max_length=20, choices=[
        ('INJURY', 'Injury'),
        ('TACTICAL', 'Tactical'),
        ('OTHER', 'Other')
    ])
    substitution_time = models.CharField(max_length=100)
    comments = models.TextField(blank=True, default='')
    approved_by = models.CharField(max_length=100, blank=True, default='')

    def clean(self):
        # Skip validation if match is not saved yet
        if not self.match_id:
            return
            
        # Only validate if both match and player_out are set
        if self.match and self.player_out:
            if not MatchPlayer.objects.filter(match=self.match, player=self.player_out).exists():
                raise ValidationError({'player_out': 'Selected player is not in the match squad'})
        
        if self.player_in == self.player_out:
            raise ValidationError({'player_in': 'Substitute player cannot be the same as player being replaced'})

    def __str__(self):
        return f"{self.player_out} replaced by {self.player_in} in {self.match}"