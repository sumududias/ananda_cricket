from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Player, Match, MatchPlayer, Team, Tournament, Substitution, TeamStanding

class MatchPlayerInlineForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        innings = cleaned_data.get('innings')
        match = cleaned_data.get('match')
        
        if innings == 2 and match and match.match_format != 'TEST':
            raise ValidationError("Second innings is only allowed for Test matches")
        return cleaned_data

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    form = MatchPlayerInlineForm
    extra = 0
    fields = (
        'player', 'innings', 'batting_order', 
        ('runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out'),
        ('overs_bowled', 'runs_conceded', 'wickets_taken', 'wide_balls', 'no_balls'),
        ('catches', 'stumpings', 'runouts'),
        'is_playing_xi'
    )

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.match_format != 'TEST':
            fields.remove('innings')
        return fields

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
    list_display = ('date', 'opponent', 'match_format', 'match_type', 'venue', 'result')
    list_filter = ('match_format', 'match_type', 'venue', 'result', 'tournament')
    inlines = [MatchPlayerInline, SubstitutionInline]
    search_fields = ('opponent', 'venue')
    
    fieldsets = (
        ('Match Details', {
            'fields': (
                'date', 'team', 'opponent', 'venue', 
                'match_format', 'match_type', 'tournament'
            )
        }),
        ('Toss & Result', {
            'fields': ('toss_winner', 'toss_decision', 'result')
        }),
        ('Additional Info', {
            'fields': ('man_of_match', 'summary', 'scorecard_photo')
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'coach', 'captain')
    search_fields = ('name', 'coach')
    raw_id_fields = ('captain',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    form = MatchPlayerInlineForm
    list_display = ('match', 'player', 'innings', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'player', 'innings', 'is_playing_xi')
    search_fields = ('player__first_name', 'player__last_name')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Match Info', {
                'fields': ['match', 'player', 'is_playing_xi']
            }),
            ('Batting', {
                'fields': ('batting_order', 'runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out')
            }),
            ('Bowling', {
                'fields': ('overs_bowled', 'runs_conceded', 'wickets_taken', 'wide_balls', 'no_balls')
            }),
            ('Fielding', {
                'fields': ('catches', 'stumpings', 'runouts')
            })
        ]
        
        # Only show innings field for test matches
        if obj and obj.match.match_format == 'TEST':
            fieldsets[0][1]['fields'].insert(2, 'innings')
            
        return fieldsets

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
