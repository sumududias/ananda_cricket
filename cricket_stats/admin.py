from django.contrib import admin
from .models import Player, Match, MatchPlayer, Team

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    extra = 0

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_role', 'batting_style', 'bowling_style')
    list_filter = ('primary_role', 'batting_style', 'is_active')
    search_fields = ('first_name', 'last_name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'opponent', 'venue', 'match_type', 'result')
    list_filter = ('match_type', 'venue', 'result')
    inlines = [MatchPlayerInline]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'coach')
    search_fields = ('name', 'coach')

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken', 'is_playing_xi')
    list_filter = ('match', 'player', 'is_playing_xi')
    search_fields = ('player__first_name', 'player__last_name')
