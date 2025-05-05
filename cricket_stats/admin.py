from django.contrib import admin
from .models import Player, Match, Team, MatchPlayer, Substitution, Tournament, TeamStanding

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_role')
    search_fields = ('first_name', 'last_name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'opponent', 'result')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'coach')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'start_date', 'end_date')
