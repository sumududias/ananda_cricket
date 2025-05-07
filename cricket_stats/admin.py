from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.html import format_html
from .models import Player, Match, MatchPlayer, Team, Tournament, Substitution, TeamStanding

# Customize admin site
admin.site.site_header = "Ananda College Cricket Statistics Administration"
admin.site.site_title = "Ananda Cricket Admin"
admin.site.index_title = "Cricket Statistics Management"

class MatchPlayerInlineForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        innings = cleaned_data.get('innings')
        match = cleaned_data.get('match')
        
        if match and match.match_format in ['T20', 'ODI']:
            cleaned_data['innings'] = 1  # Force innings to 1 for T20/ODI
        elif innings == 2 and match and match.match_format != 'TEST':
            raise ValidationError("Second innings is only allowed for Test matches")
            
        return cleaned_data
        
    class Meta:
        model = MatchPlayer
        fields = '__all__'

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    form = MatchPlayerInlineForm
    extra = 1
    
    def get_fieldsets(self, request, obj=None):
        if obj and obj.match_format in ['T20', 'ODI']:
            return [(None, {'fields': (
                'player', 'batting_order',
                ('runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out'),
                ('overs_bowled', 'runs_conceded', 'wickets_taken', 'maidens', 'wide_balls', 'no_balls'),
                ('catches', 'stumpings', 'runouts'),
                'is_playing_xi'
            )})]
        return [(None, {'fields': (
            'player', 'innings', 'batting_order',
            ('runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out'),
            ('overs_bowled', 'runs_conceded', 'wickets_taken', 'maidens', 'wide_balls', 'no_balls'),
            ('catches', 'stumpings', 'runouts'),
            'is_playing_xi'
        )})]

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj and obj.match_format in ['T20', 'ODI']:
            fields.remove('innings')
        return fields

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 0
    fk_name = 'match'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'opponent', 'venue')
    list_filter = ('match_format', 'match_type', 'venue', 'result', 'tournament')
    inlines = [MatchPlayerInline, SubstitutionInline]
    search_fields = ('opponent', 'venue')
    
    fieldsets = (
        ('Match Details', {
            'fields': (
                ('date', 'match_format'),
                ('team', 'opponent'),
                ('venue', 'match_type'),
                'tournament'
            )
        }),
        ('Toss & Result', {
            'fields': (('toss_winner', 'toss_decision'), 'result')
        }),
        ('Additional Info', {
            'fields': ('man_of_match', 'summary', 'scorecard_photo')
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = ('admin/js/jquery.init.js', 'admin/js/inlines.js')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season')
    search_fields = ('name',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'player')
    search_fields = ('player__first_name', 'player__last_name')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'season')
    search_fields = ('name',)

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
