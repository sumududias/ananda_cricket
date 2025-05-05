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
    list_display = ('date', 'opponent', 'venue', 'match_type', 'result')
    list_filter = ('match_type', 'venue', 'result', 'tournament')
    inlines = [MatchPlayerInline, SubstitutionInline]
    search_fields = ('opponent', 'venue')

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
