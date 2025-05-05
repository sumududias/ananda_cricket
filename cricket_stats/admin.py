from django.contrib import admin
from .models import Player, Match, MatchPlayer, Team, Tournament, Substitution, TeamStanding

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    extra = 0

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 0
    fk_name = 'match'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_role', 'batting_style', 'bowling_style')
    list_filter = ('primary_role', 'batting_style', 'is_active')
    search_fields = ('first_name', 'last_name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'opponent', 'venue', 'match_type', 'result', 'ananda_total_extras', 'opponent_total_extras')
    list_filter = ('match_type', 'venue', 'result', 'tournament')
    inlines = [MatchPlayerInline, SubstitutionInline]
    search_fields = ('opponent', 'venue')
    
    fieldsets = (
        ('Match Details', {
            'fields': ('date', 'team', 'opponent', 'venue', 'match_type', 'tournament')
        }),
        ('Toss & Result', {
            'fields': ('toss_winner', 'toss_decision', 'result')
        }),
        ('Ananda Extras', {
            'fields': (
                'ananda_extras_byes', 'ananda_extras_leg_byes',
                'ananda_extras_wides', 'ananda_extras_no_balls',
                'ananda_extras_penalty'
            )
        }),
        ('Opponent Extras', {
            'fields': (
                'opponent_extras_byes', 'opponent_extras_leg_byes',
                'opponent_extras_wides', 'opponent_extras_no_balls',
                'opponent_extras_penalty'
            )
        }),
        ('Final Scores', {
            'fields': ('ananda_score', 'opponent_score', 'man_of_match')
        }),
        ('Additional Info', {
            'fields': ('summary', 'scorecard_photo')
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'coach', 'captain')
    search_fields = ('name', 'coach')
    raw_id_fields = ('captain',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken', 'is_playing_xi')
    list_filter = ('match', 'player', 'is_playing_xi')
    search_fields = ('player__first_name', 'player__last_name')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'start_date', 'end_date', 'organizer')
    list_filter = ('season',)
    search_fields = ('name', 'organizer')

@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_out', 'player_in', 'reason', 'substitution_time')
    list_filter = ('reason', 'match')
    search_fields = ('player_out__first_name', 'player_out__last_name', 'player_in__first_name', 'player_in__last_name')

@admin.register(TeamStanding)
class TeamStandingAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'team', 'matches_played', 'matches_won', 'matches_lost', 'points', 'position')
    list_filter = ('tournament', 'team')
    search_fields = ('tournament__name', 'team__name')
