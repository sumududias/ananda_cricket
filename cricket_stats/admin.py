from django.contrib import admin
from .models import Player, Match, MatchPlayer, Team

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    extra = 0

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'role', 'batting_style', 'bowling_style')
    list_filter = ('team', 'role')
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_date', 'team1', 'team2', 'venue', 'match_type')
    list_filter = ('match_type', 'venue')
    inlines = [MatchPlayerInline]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'player')
    search_fields = ('player__name',)
