from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Q, Max

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
    batting_style = models.CharField(max_length=20, choices=[('R', 'Right-handed'), ('L', 'Left-handed')])
    bowling_style = models.CharField(max_length=50, blank=True, null=True)
    primary_role = models.CharField(max_length=4, choices=ROLES)
    player_class = models.CharField(max_length=20)
    year_joined = models.IntegerField()
    photo = models.ImageField(upload_to='players/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def total_matches(self):
        return self.matchplayer_set.filter(is_playing_xi=True).count()

    @property
    def batting_stats(self):
        matches = self.matchplayer_set.filter(is_playing_xi=True)
        
        stats = matches.aggregate(
            total_matches=models.Count('match', distinct=True),
            total_runs=models.Sum('runs_scored'),
            total_balls=models.Sum('balls_faced'),
            total_fours=models.Sum('fours'),
            total_sixes=models.Sum('sixes'),
            innings=models.Count('id', filter=models.Q(batting_order__isnull=False)),
            not_outs=models.Count('id', filter=models.Q(how_out='Not Out') | models.Q(how_out__isnull=True)),
            highest_score=models.Max('runs_scored')
        )
        
        total_runs = stats['total_runs'] or 0
        total_balls = stats['total_balls'] or 0
        innings = stats['innings'] or 0
        not_outs = stats['not_outs'] or 0
        
        # Calculate batting average and strike rate
        if innings - not_outs > 0:
            batting_average = total_runs / (innings - not_outs)
        else:
            batting_average = total_runs if total_runs > 0 else 0
            
        if total_balls > 0:
            strike_rate = (total_runs * 100.0) / total_balls
        else:
            strike_rate = 0
        
        return {
            'matches': stats['total_matches'] or 0,
            'innings': innings,
            'not_outs': not_outs,
            'runs': total_runs,
            'balls_faced': total_balls,
            'fours': stats['total_fours'] or 0,
            'sixes': stats['total_sixes'] or 0,
            'average': round(batting_average, 2),
            'strike_rate': round(strike_rate, 2),
            'highest_score': stats['highest_score'] or 0
        }
        
    @property
    def bowling_stats(self):
        matches = self.matchplayer_set.filter(is_playing_xi=True)
        
        stats = matches.aggregate(
            total_matches=models.Count('match', distinct=True),
            total_overs=models.Sum('overs_bowled'),
            total_runs=models.Sum('runs_conceded'),
            total_wickets=models.Sum('wickets_taken'),
            total_maidens=models.Sum('maidens'),
            total_wides=models.Sum('wide_balls'),
            total_no_balls=models.Sum('no_balls'),
            innings=models.Count('id', filter=models.Q(overs_bowled__gt=0))
        )
        
        total_overs = stats['total_overs'] or 0
        total_runs = stats['total_runs'] or 0
        total_wickets = stats['total_wickets'] or 0
        
        # Calculate bowling average and economy rate
        if total_wickets > 0:
            bowling_average = total_runs / total_wickets
        else:
            bowling_average = 0
            
        if total_overs > 0:
            economy_rate = total_runs / total_overs
        else:
            economy_rate = 0
            
        return {
            'matches': stats['total_matches'] or 0,
            'innings': stats['innings'] or 0,
            'overs': total_overs,
            'runs': total_runs,
            'wickets': total_wickets,
            'maidens': stats['total_maidens'] or 0,
            'wides': stats['total_wides'] or 0,
            'no_balls': stats['total_no_balls'] or 0,
            'average': round(bowling_average, 2),
            'economy': round(economy_rate, 2),
            'best_bowling': self._get_best_bowling()
        }
        
    @property
    def fielding_stats(self):
        matches = self.matchplayer_set.filter(is_playing_xi=True)
        
        stats = matches.aggregate(
            total_matches=models.Count('match', distinct=True),
            total_catches=models.Sum('catches'),
            total_stumpings=models.Sum('stumpings'),
            total_runouts=models.Sum('runouts')
        )
        
        return {
            'matches': stats['total_matches'] or 0,
            'catches': stats['total_catches'] or 0,
            'stumpings': stats['total_stumpings'] or 0,
            'runouts': stats['total_runouts'] or 0
        }

    def _get_best_bowling(self):
        best = self.matchplayer_set.filter(
            is_playing_xi=True,
            wickets_taken__gt=0
        ).order_by('-wickets_taken', 'runs_conceded').first()

        if best:
            return f"{best.wickets_taken}/{best.runs_conceded}"
        return "0/0"

    def get_batting_stats(self):
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
            stats['economy'] = float(total_runs) / total_overs
        else:
            stats['economy'] = 0.0

        # Calculate strike rate
        if total_wickets > 0:
            stats['strike_rate'] = (total_overs * 6) / total_wickets
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
                player=self
            )
            
            if not matches.exists():
                return None
                
            total_runs = matches.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
            total_balls = matches.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0
            total_wickets = matches.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
            total_matches = matches.values('match').distinct().count()
            highest_score = matches.aggregate(Max('runs_scored'))['runs_scored__max'] or 0
            centuries = matches.filter(is_century=True).count()
            half_centuries = matches.filter(is_half_century=True).count()
            
            # Calculate bowling stats
            total_overs = matches.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
            runs_conceded = matches.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] or 0
            wides = matches.aggregate(Sum('wide_balls'))['wide_balls__sum'] or 0
            no_balls = matches.aggregate(Sum('no_balls'))['no_balls__sum'] or 0
            
            # Calculate averages safely
            try:
                batting_average = round(total_runs / total_matches, 2) if total_matches > 0 else 0
            except:
                batting_average = 0
                
            try:
                strike_rate = round((total_runs * 100) / total_balls, 2) if total_balls > 0 else 0
            except:
                strike_rate = 0
                
            try:
                bowling_average = round(runs_conceded / total_wickets, 2) if total_wickets > 0 else 0
            except:
                bowling_average = 0
                
            try:
                economy_rate = round(runs_conceded / total_overs, 2) if total_overs > 0 else 0
            except:
                economy_rate = 0
            
            return {
                'format': format_type,
                'matches': total_matches,
                'batting': {
                    'runs': total_runs,
                    'balls': total_balls,
                    'average': batting_average,
                    'strike_rate': strike_rate,
                    'highest_score': highest_score,
                    'centuries': centuries,
                    'half_centuries': half_centuries,
                },
                'bowling': {
                    'wickets': total_wickets,
                    'overs': total_overs,
                    'runs_conceded': runs_conceded,
                    'average': bowling_average,
                    'economy': economy_rate,
                    'wides': wides,
                    'no_balls': no_balls,
                }
            }
        except Exception as e:
            print(f"Error calculating stats for {self}: {str(e)}")
            return None

    @property
    def test_stats(self):
        return self.get_format_stats('TEST')
        
    @property
    def odi_stats(self):
        return self.get_format_stats('ODI')
        
    @property
    def t20_stats(self):
        return self.get_format_stats('T20')

class Team(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20)
    coach = models.CharField(max_length=100)
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='captain_of')

    def __str__(self):
        return f"{self.name} ({self.season})"

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    organizer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.season}"

class Match(models.Model):
    MATCH_TYPE_CHOICES = [
        ('TOURNAMENT', 'Tournament'),
        ('FRIENDLY', 'Friendly')
    ]
    
    MATCH_FORMAT_CHOICES = [
        ('T20', 'Twenty20'),
        ('ODI', 'One Day (50 Overs)'),
        ('TEST', 'Test Match')
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    opponent = models.CharField(max_length=100)
    date = models.DateField()
    venue = models.CharField(max_length=100)
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES)
    match_format = models.CharField(max_length=4, choices=MATCH_FORMAT_CHOICES, default='T20')
    tournament = models.ForeignKey('Tournament', on_delete=models.SET_NULL, null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    man_of_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Extras
    ananda_extras_byes = models.IntegerField(default=0, verbose_name='Byes')
    ananda_extras_leg_byes = models.IntegerField(default=0, verbose_name='Leg Byes')
    opponent_extras_byes = models.IntegerField(default=0, verbose_name='Opponent Byes')
    opponent_extras_leg_byes = models.IntegerField(default=0, verbose_name='Opponent Leg Byes')

    def __str__(self):
        return f"{self.get_match_format_display()} vs {self.opponent} on {self.date}"

    @property
    def is_test_match(self):
        return self.match_format == 'TEST'

    @property
    def max_innings(self):
        """Return the maximum number of innings allowed for this match format"""
        return 2 if self.match_format == 'TEST' else 1

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Validate that no players have innings > 1 for non-TEST matches
        if self.match_format in ['T20', 'ODI']:
            invalid_players = self.matchplayer_set.filter(innings__gt=1)
            if invalid_players.exists():
                raise ValidationError("Only TEST matches can have second innings")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # If match format is changed from TEST to T20/ODI, update all players to innings 1
        if self.match_format in ['T20', 'ODI']:
            self.matchplayer_set.filter(innings__gt=1).update(innings=1)

    @property
    def ananda_total_extras(self):
        """Calculate total extras for Ananda team"""
        player_extras = self.matchplayer_set.filter(
            innings=1
        ).aggregate(
            total_wides=Sum('wide_balls', default=0),
            total_no_balls=Sum('no_balls', default=0)
        )
        return (
            self.ananda_extras_byes +
            self.ananda_extras_leg_byes +
            player_extras['total_wides'] +
            player_extras['total_no_balls']
        )

    @property
    def opponent_total_extras(self):
        """Calculate total extras for opponent team"""
        player_extras = self.matchplayer_set.filter(
            innings=2
        ).aggregate(
            total_wides=Sum('wide_balls', default=0),
            total_no_balls=Sum('no_balls', default=0)
        )
        return (
            self.opponent_extras_byes +
            self.opponent_extras_leg_byes +
            player_extras['total_wides'] +
            player_extras['total_no_balls']
        )

class MatchPlayer(models.Model):
    INNINGS_CHOICES = [
        (1, 'First Innings'),
        (2, 'Second Innings'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    innings = models.IntegerField(choices=INNINGS_CHOICES, default=1)
    batting_order = models.IntegerField(null=True, blank=True)
    runs_scored = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    how_out = models.CharField(max_length=50, null=True, blank=True)
    
    # Bowling stats
    overs_bowled = models.FloatField(default=0)
    runs_conceded = models.IntegerField(default=0)
    wickets_taken = models.IntegerField(default=0)
    wide_balls = models.IntegerField(default=0)
    no_balls = models.IntegerField(default=0)
    maidens = models.IntegerField(default=0)
    
    # Fielding stats
    catches = models.IntegerField(default=0)
    stumpings = models.IntegerField(default=0)
    runouts = models.IntegerField(default=0)
    
    is_playing_xi = models.BooleanField(default=True)
    is_substitute = models.BooleanField(default=False)
    
    # Auto-calculated fields
    is_century = models.BooleanField(default=False)
    is_half_century = models.BooleanField(default=False)

    class Meta:
        unique_together = ['match', 'player', 'innings']
        ordering = ['innings', 'batting_order']

    def __str__(self):
        return f"{self.player} - {self.match} ({self.get_innings_display()})"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.innings == 2 and not self.match.is_test_match:
            raise ValidationError("Second innings is only allowed for Test matches")
        
    def save(self, *args, **kwargs):
        self.clean()
        # Auto-calculate century and half-century
        if self.runs_scored >= 100:
            self.is_century = True
            self.is_half_century = False
        elif self.runs_scored >= 50:
            self.is_half_century = True
            self.is_century = False
        else:
            self.is_century = False
            self.is_half_century = False
        super().save(*args, **kwargs)

class Substitution(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_out = models.ForeignKey(Player, related_name='substituted_out', on_delete=models.CASCADE)
    player_in = models.ForeignKey(Player, related_name='substituted_in', on_delete=models.CASCADE)
    reason = models.CharField(max_length=100, choices=[
        ('INJURY', 'Injury'),
        ('TACTICAL', 'Tactical'),
        ('OTHER', 'Other')
    ])
    comments = models.TextField(blank=True, null=True)
    substitution_time = models.CharField(max_length=50)
    approved_by = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.player_out} → {self.player_in} in {self.match}"

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