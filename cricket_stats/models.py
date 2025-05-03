from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Q

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
        print(f"DEBUG - Batting - Raw matches query: {matches.query}")
        
        stats = matches.aggregate(
            total_runs=Sum('runs_scored'),
            total_balls=Sum('balls_faced'),
            total_fours=Sum('fours'),
            total_sixes=Sum('sixes'),
            innings=Count('id', filter=Q(batting_order__isnull=False)),
            not_outs=Count('id', filter=Q(how_out='Not Out') | Q(how_out__isnull=True))
        )
        
        print(f"DEBUG - Batting - Raw stats from DB: {stats}")
        
        total_runs = float(stats['total_runs'] or 0)
        total_balls = float(stats['total_balls'] or 0)
        innings = int(stats['innings'] or 0)
        not_outs = int(stats['not_outs'] or 0)
        outs = innings - not_outs

        # Calculate batting average
        batting_average = float(total_runs) / float(outs) if outs > 0 else float(total_runs) if total_runs > 0 else 0.0

        # Calculate strike rate
        strike_rate = (float(total_runs) * 100.0) / float(total_balls) if total_balls > 0 else 0.0

        result = {
            'matches': self.total_matches,
            'innings': innings,
            'not_outs': not_outs,
            'runs': int(total_runs),
            'balls_faced': int(total_balls),
            'fours': int(stats['total_fours'] or 0),
            'sixes': int(stats['total_sixes'] or 0),
            'average': float(round(batting_average, 2)),
            'strike_rate': float(round(strike_rate, 2)),
            'highest_score': int(matches.aggregate(highest=models.Max('runs_scored'))['highest'] or 0),
        }
        
        print(f"DEBUG - Batting - Final stats: {result}")
        return result

    @property
    def bowling_stats(self):
        matches = self.matchplayer_set.filter(is_playing_xi=True)
        print(f"DEBUG - Bowling - Raw matches query: {matches.query}")
        
        stats = matches.aggregate(
            total_overs=Sum('overs_bowled'),
            total_runs=Sum('runs_conceded'),
            total_wickets=Sum('wickets_taken'),
            innings=Count('id', filter=Q(overs_bowled__gt=0))
        )
        
        print(f"DEBUG - Bowling - Raw stats from DB: {stats}")

        total_overs = stats['total_overs'] or 0
        total_runs = stats['total_runs'] or 0
        total_wickets = stats['total_wickets'] or 0
        innings = stats['innings'] or 0

        # Calculate bowling average
        bowling_average = total_runs / total_wickets if total_wickets > 0 else 0

        # Calculate economy rate
        economy_rate = total_runs / total_overs if total_overs > 0 else 0

        # Calculate strike rate
        bowling_strike_rate = (total_overs * 6) / total_wickets if total_wickets > 0 else 0

        result = {
            'matches': self.total_matches,
            'innings': innings,
            'overs': total_overs,
            'runs': total_runs,
            'wickets': total_wickets,
            'average': round(bowling_average, 2),
            'economy': round(economy_rate, 2),
            'strike_rate': round(bowling_strike_rate, 2),
            'best_bowling': self._get_best_bowling(),
        }
        
        print(f"DEBUG - Bowling - Final stats: {result}")
        return result

    def _get_best_bowling(self):
        best = self.matchplayer_set.filter(
            is_playing_xi=True,
            wickets_taken__gt=0
        ).order_by('-wickets_taken', 'runs_conceded').first()

        if best:
            return f"{best.wickets_taken}/{best.runs_conceded}"
        return "0/0"

    @property
    def fielding_stats(self):
        stats = self.matchplayer_set.filter(is_playing_xi=True).aggregate(
            total_catches=Sum('catches'),
            total_stumpings=Sum('stumpings'),
            total_runouts=Sum('runouts')
        )

        return {
            'matches': self.total_matches,
            'catches': stats['total_catches'] or 0,
            'stumpings': stats['total_stumpings'] or 0,
            'runouts': stats['total_runouts'] or 0,
        }

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
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    opponent = models.CharField(max_length=100)
    date = models.DateField()
    venue = models.CharField(max_length=100)
    match_type = models.CharField(max_length=20, choices=[('TOURNAMENT', 'Tournament'), ('FRIENDLY', 'Friendly')])
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)
    toss_winner = models.CharField(max_length=100)
    toss_decision = models.CharField(max_length=10, choices=[('BAT', 'Bat'), ('BOWL', 'Bowl')])
    result = models.CharField(max_length=10, choices=[('WON', 'Won'), ('LOST', 'Lost'), ('DRAW', 'Draw')])
    ananda_score = models.CharField(max_length=50)
    opponent_score = models.CharField(max_length=50)
    summary = models.TextField()
    man_of_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    scorecard_photo = models.ImageField(upload_to='scorecards/', blank=True, null=True)  # For proof

    def __str__(self):
        return f"vs {self.opponent} on {self.date}"

class MatchPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    batting_order = models.IntegerField(null=True, blank=True)
    runs_scored = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    how_out = models.CharField(max_length=50, blank=True, null=True)
    overs_bowled = models.FloatField(default=0)
    runs_conceded = models.IntegerField(default=0)
    wickets_taken = models.IntegerField(default=0)
    catches = models.IntegerField(default=0)
    stumpings = models.IntegerField(default=0)
    runouts = models.IntegerField(default=0)
    is_playing_xi = models.BooleanField(default=True)
    is_substitute = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player} in {self.match}"

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