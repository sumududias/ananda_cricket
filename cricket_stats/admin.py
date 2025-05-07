from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django import forms
from django.utils.html import format_html
from .models import Player, Match, MatchPlayer, Team, Tournament, Substitution, TeamStanding

# Customize admin site
admin.site.site_header = "Ananda College Cricket Statistics Administration"
admin.site.site_title = "Ananda Cricket Admin"
admin.site.index_title = "Cricket Statistics Management"

class MatchPlayerInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'instance') and self.instance.match and self.instance.match.match_format in ['T20', 'ODI']:
            self.fields['innings'].widget = forms.HiddenInput()
            self.fields['innings'].initial = 1

    def clean(self):
        cleaned_data = super().clean()
        match = cleaned_data.get('match') or (self.instance.match if self.instance else None)
        
        if match and match.match_format in ['T20', 'ODI']:
            cleaned_data['innings'] = 1
        elif cleaned_data.get('innings') == 2 and match and match.match_format != 'TEST':
            raise ValidationError("Second innings is only allowed for Test matches")
        
        return cleaned_data
    
    class Meta:
        model = MatchPlayer
        fields = '__all__'

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    form = MatchPlayerInlineForm
    extra = 1
    
    fields = (
        'player', 'innings', 'batting_order',
        ('runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out'),
        ('overs_bowled', 'runs_conceded', 'wickets_taken', 'maidens', 'wide_balls', 'no_balls'),
        ('catches', 'stumpings', 'runouts'),
        'is_playing_xi'
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.match_format in ['T20', 'ODI']:
            fields = list(self.fields)
            fields.remove('innings')
            self.fields = tuple(fields)
        return formset

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 1

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'team', 'opponent', 'match_format', 'result')
    list_filter = ('match_format', 'match_type', 'tournament')
    search_fields = ('team__name', 'opponent')
    inlines = [MatchPlayerInline, SubstitutionInline]
    
    fieldsets = [
        (None, {
            'fields': (
                ('team', 'opponent'),
                ('date', 'venue'),
                ('match_format', 'match_type'),
                'tournament',
                'result',
                'man_of_match',
            )
        }),
        ('Extras', {
            'fields': (
                ('ananda_extras_byes', 'ananda_extras_leg_byes'),
                ('opponent_extras_byes', 'opponent_extras_leg_byes'),
            ),
            'classes': ('collapse',)
        })
    ]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'batting_style', 'bowling_style')
    search_fields = ('first_name', 'last_name')
    list_filter = ('batting_style',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'captain')
    search_fields = ('name',)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'start_date', 'end_date')
    search_fields = ('name',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'player')
    search_fields = ('player__first_name', 'player__last_name')
    form = MatchPlayerInlineForm

@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_out', 'player_in', 'substitution_time')
    list_filter = ('match',)
    search_fields = ('player_out__first_name', 'player_out__last_name', 'player_in__first_name', 'player_in__last_name')

@admin.register(TeamStanding)
class TeamStandingAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'team', 'matches_played', 'matches_won', 'matches_lost', 'points', 'position')
    list_filter = ('tournament', 'team')
    search_fields = ('team__name', 'tournament__name')
