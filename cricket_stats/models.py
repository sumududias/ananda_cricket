from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Q, Max
from django.core.exceptions import ValidationError

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
    batting_style = models.CharField(max_length=20, choices=[('R', 'Right-handed'), ('L', 'Left-handed')])
    bowling_style = models.CharField(max_length=50, blank=True, null=True)
    primary_role = models.CharField(max_length=4, choices=ROLES)
    player_class = models.CharField(max_length=20)
    year_joined = models.IntegerField()
    is_active = models.BooleanField(default=True)

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
            'runs': total_runs,
            'wickets': total_wickets,
            'batting_avg': round(batting_average, 2),
            'bowling_avg': round(bowling_average, 2),
            'centuries': matches.filter(is_century=True).count(),
            'fifties': matches.filter(is_half_century=True).count(),
        }
    
    @property
    def t20_format_stats(self):
        return self.get_format_specific_stats('T20')
    
    @property
    def odi_format_stats(self):
        return self.get_format_specific_stats('ODI')
    
    @property
    def test_format_stats(self):
        return self.get_format_specific_stats('TEST')

    def get_stats_by_format(self, match_format):
        """Get player statistics for a specific match format"""
        match_players = self.matchplayer_set.filter(match__match_format=match_format)
        
        if not match_players.exists():
            return None

        # Batting stats
        total_runs = match_players.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
        total_innings = match_players.exclude(how_out='DNB').count()
        not_outs = match_players.filter(how_out='NO').count()
        balls_faced = match_players.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0
        fours = match_players.aggregate(Sum('fours'))['fours__sum'] or 0
        sixes = match_players.aggregate(Sum('sixes'))['sixes__sum'] or 0
        highest_score = match_players.aggregate(Max('runs_scored'))['runs_scored__max'] or 0
        
        # Calculate batting average and strike rate
        batting_average = total_runs / (total_innings - not_outs) if total_innings > not_outs else 0
        strike_rate = (total_runs / balls_faced * 100) if balls_faced > 0 else 0
        
        # Count fifties and hundreds
        fifties = match_players.filter(runs_scored__gte=50, runs_scored__lt=100).count()
        hundreds = match_players.filter(runs_scored__gte=100).count()

        # Bowling stats
        total_wickets = match_players.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
        total_runs_conceded = match_players.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] or 0
        total_overs = match_players.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
        total_maidens = match_players.aggregate(Sum('maidens'))['maidens__sum'] or 0
        
        # Calculate bowling average, economy, and strike rate
        bowling_average = total_runs_conceded / total_wickets if total_wickets > 0 else 0
        economy_rate = float(total_runs_conceded) / float(total_overs) if total_overs > 0 else 0
        bowling_strike_rate = (float(total_overs * 6) / float(total_wickets)) if total_wickets > 0 else 0
        
        # Count five wicket hauls
        five_wickets = match_players.filter(wickets_taken__gte=5).count()

        # Fielding stats
        total_catches = match_players.aggregate(Sum('catches'))['catches__sum'] or 0
        total_stumpings = match_players.aggregate(Sum('stumpings'))['stumpings__sum'] or 0
        total_runouts = match_players.aggregate(Sum('runouts'))['runouts__sum'] or 0

        return {
            'batting': {
                'matches': match_players.values('match').distinct().count(),
                'innings': total_innings,
                'not_outs': not_outs,
                'runs': total_runs,
                'balls': balls_faced,
                'highest_score': highest_score,
                'average': round(batting_average, 2),
                'strike_rate': round(strike_rate, 2),
                'fifties': fifties,
                'hundreds': hundreds,
                'fours': fours,
                'sixes': sixes
            },
            'bowling': {
                'overs': total_overs,
                'maidens': total_maidens,
                'runs': total_runs_conceded,
                'wickets': total_wickets,
                'average': round(bowling_average, 2),
                'economy': round(economy_rate, 2),
                'strike_rate': round(bowling_strike_rate, 2),
                'five_wickets': five_wickets
            },
            'fielding': {
                'catches': total_catches,
                'stumpings': total_stumpings,
                'runouts': total_runouts
            }
        }

    def test_stats(self):
        """Get player statistics for Test matches"""
        return self.get_stats_by_format('TEST')

    def odi_stats(self):
        """Get player statistics for ODI matches"""
        return self.get_stats_by_format('ODI')

    def t20_stats(self):
        """Get player statistics for T20 matches"""
        return self.get_stats_by_format('T20')

class Match(models.Model):
    MATCH_FORMATS = [
        ('TEST', 'Test Match'),
        ('ODI', 'One Day International'),
        ('T20', 'Twenty20'),
    ]
    
    team = models.CharField(max_length=100, default='Ananda College')
    opponent = models.CharField(max_length=100)
    match_date = models.DateField()
    venue = models.CharField(max_length=100, null=True, blank=True)
    format = models.CharField(max_length=4, choices=MATCH_FORMATS, default='ODI')
    toss_winner = models.CharField(max_length=100, null=True, blank=True)
    toss_decision = models.CharField(max_length=10, null=True, blank=True)
    result = models.CharField(max_length=200, null=True, blank=True)
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
    opponent_second_innings = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['-match_date']

    def clean(self):
        if self.format not in [f[0] for f in self.MATCH_FORMATS]:
            raise ValidationError('Invalid match format')
        
        # Reset second innings totals for non-test matches
        if self.format != 'TEST':
            self.second_innings_total = 0
            self.opponent_second_innings = 0

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate and update match totals"""
        first_innings = self.matchplayer_set.filter(innings_number=1)
        self.first_innings_total = sum(p.runs_scored or 0 for p in first_innings)
        
        if self.format == 'TEST':
            second_innings = self.matchplayer_set.filter(innings_number=2)
            self.second_innings_total = sum(p.runs_scored or 0 for p in second_innings)
        else:
            self.second_innings_total = 0
            self.opponent_second_innings = 0
        
        self.save()

    def __str__(self):
        return f"{self.team} vs {self.opponent} - {self.match_date}"

class MatchPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    innings_number = models.IntegerField(default=1)
    batting_order = models.IntegerField(null=True, blank=True)
    runs_scored = models.IntegerField(null=True, blank=True)
    balls_faced = models.IntegerField(null=True, blank=True)
    fours = models.IntegerField(null=True, blank=True)
    sixes = models.IntegerField(null=True, blank=True)
    how_out = models.CharField(max_length=100, null=True, blank=True)
    overs_bowled = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    maidens = models.IntegerField(null=True, blank=True)
    runs_conceded = models.IntegerField(null=True, blank=True)
    wickets_taken = models.IntegerField(null=True, blank=True)
    wide_balls = models.IntegerField(null=True, blank=True)
    no_balls = models.IntegerField(null=True, blank=True)
    catches = models.IntegerField(null=True, blank=True)
    stumpings = models.IntegerField(null=True, blank=True)
    runouts = models.IntegerField(null=True, blank=True)
    is_playing_xi = models.BooleanField(default=True)
    is_substitute = models.BooleanField(default=False)
    selection_notes = models.TextField(null=True, blank=True)
    approved_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('match', 'player', 'innings_number')

    def __str__(self):
        return f"{self.player.name} - {self.match}"

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

class BattingInnings(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    innings_number = models.IntegerField(default=1)
    batting_position = models.IntegerField()
    runs_scored = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    how_out = models.CharField(max_length=100, blank=True, null=True)
    bowler = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='wickets_taken_set')
    fielder = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='catches_taken_set')

    class Meta:
        unique_together = ('match', 'player', 'innings_number')
        ordering = ['innings_number', 'batting_position']

    def __str__(self):
        return f"{self.player} - {self.match} - Innings {self.innings_number}"

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

    class Meta:
        unique_together = ('match', 'player', 'innings_number')
        ordering = ['innings_number']

    def __str__(self):
        return f"{self.player} - {self.match} - Innings {self.innings_number}"

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