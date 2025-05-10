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
    class Meta:
        model = MatchPlayer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.pk:  # Editing existing record
            self.fields['innings_number'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        player = cleaned_data.get('player')
        innings = cleaned_data.get('innings_number')
        
        # For new records, check if this player is already added to this innings
        if not self.instance.pk and player and innings:
            # Get the parent form's instance (Match)
            parent_form = self.parent_form.instance if hasattr(self, 'parent_form') else None
            formset = self.parent_form if hasattr(self, 'parent_form') else None
            
            # Check other forms in the formset for duplicates
            if formset:
                for form in formset.forms:
                    if form != self and not form.cleaned_data.get('DELETE'):
                        other_player = form.cleaned_data.get('player')
                        other_innings = form.cleaned_data.get('innings_number')
                        if player == other_player and innings == other_innings:
                            raise forms.ValidationError(
                                f"Player {player} is already added to innings {innings}"
                            )
        
        return cleaned_data

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    form = MatchPlayerInlineForm
    extra = 1
    fields = ['player', 'innings_number', 'batting_order', 'selection_notes', 'approved_by',
             'runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out', 
             'overs_bowled', 'maidens', 'runs_conceded', 'wickets_taken', 
             'wide_balls', 'no_balls', 'catches', 'stumpings', 'runouts']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.match_format != 'TEST':
            # For non-TEST matches, only show 1st innings
            formset.form.base_fields['innings_number'].widget.choices = [
                (1, '1st Innings'),
            ]
        else:
            formset.form.base_fields['innings_number'].widget.choices = [
                (1, '1st Innings'),
                (2, '2nd Innings'),
            ]
        return formset

    def save_formset(self, request, form, formset, change):
        if formset.model == MatchPlayer:
            instances = formset.save(commit=False)
            for instance in instances:
                # For new players, set default innings number
                if not instance.pk and not instance.innings_number:
                    instance.innings_number = 1
                instance.save()
            formset.save_m2m()
        else:
            # For other formsets (like Substitution)
            formset.save()

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 1
    fields = ['player_out', 'player_in', 'reason', 'substitution_time', 'comments']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['date', 'get_team_display', 'get_opponent_display', 'match_format', 'get_result_display', 'man_of_match']
    list_filter = ['match_format', 'tournament', 'date']
    search_fields = ['team__name', 'opponent', 'tournament__name']
    inlines = [MatchPlayerInline, SubstitutionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('team', 'opponent'),
                ('date', 'venue'),
                ('match_type', 'match_format'),
                'tournament'
            )
        }),
        ('Match Result', {
            'fields': (
                'result',
                'man_of_match'
            ),
            'classes': ('wide',)
        }),
        ('Extras', {
            'fields': (
                ('ananda_extras_byes', 'ananda_extras_leg_byes'),
                ('opponent_extras_byes', 'opponent_extras_leg_byes'),
            ),
            'classes': ('collapse',)
        })
    )

    def get_team_display(self, obj):
        return str(obj.team) if obj.team else '-'
    get_team_display.short_description = 'Team'
    
    def get_opponent_display(self, obj):
        return obj.opponent if obj.opponent else '-'
    get_opponent_display.short_description = 'Opponent'
    
    def get_result_display(self, obj):
        if not obj.result:
            return 'Not played'
        return dict(Match.RESULT_CHOICES).get(obj.result, obj.result)
    get_result_display.short_description = 'Result'

    def save_formset(self, request, form, formset, change):
        if formset.model == MatchPlayer:
            instances = formset.save(commit=False)
            for instance in instances:
                # For new players, set default innings number
                if not instance.pk and not instance.innings_number:
                    instance.innings_number = 1
                instance.save()
            formset.save_m2m()
        else:
            # For other formsets (like Substitution)
            formset.save()

    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/inlines.js')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_photo', 'date_of_birth', 'primary_role']
    search_fields = ['first_name', 'last_name']
    list_filter = ['primary_role']
    fields = ['first_name', 'last_name', 'dob', 'photo', 'primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active']
    readonly_fields = ['display_photo_large', 'display_stats']

    def get_fieldsets(self, request, obj=None):
        if obj:  # Only show stats for existing players
            return [
                ('Personal Information', {
                    'fields': ['first_name', 'last_name', 'dob', 'photo', 'display_photo_large', 'primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active']
                }),
                ('Statistics', {
                    'fields': ['display_stats'],
                    'classes': ['wide']
                })
            ]
        return [('Personal Information', {
            'fields': ['first_name', 'last_name', 'dob', 'photo', 'primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active']
        })]

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No photo"
    display_photo.short_description = 'Photo'

    def display_photo_large(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="200" height="200" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />', obj.photo.url)
        return "No photo"
    display_photo_large.short_description = 'Player Photo'

    def display_stats(self, obj):
        if not obj:
            return ''
        
        # Get statistics for all formats
        test_stats = obj.test_stats()
        odi_stats = obj.odi_stats()
        t20_stats = obj.t20_stats()
        
        # Format the statistics HTML
        html = '<div style="max-width: 800px;">'
        
        # Test Statistics
        html += '<h3 style="color: #417690;">Test Match Statistics</h3>'
        html += self._format_stats_table(test_stats)
        
        # ODI Statistics
        html += '<h3 style="color: #417690;">ODI Statistics</h3>'
        html += self._format_stats_table(odi_stats)
        
        # T20 Statistics
        html += '<h3 style="color: #417690;">T20 Statistics</h3>'
        html += self._format_stats_table(t20_stats)
        
        html += '</div>'
        return format_html(html)
    display_stats.short_description = 'Player Statistics'

    def _format_stats_table(self, stats):
        if not stats:
            return '<p>No statistics available</p>'
            
        batting = stats.get('batting', {})
        bowling = stats.get('bowling', {})
        fielding = stats.get('fielding', {})
        
        html = '''
        <div style="max-width: 800px;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #79aec8; color: white;">
                    <th style="padding: 8px; text-align: left;" colspan="12">Batting Statistics</th>
                </tr>
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 8px; border: 1px solid #ddd;">M</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Inn</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">NO</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Runs</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">HS</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Avg</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">SR</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">50s</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">100s</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">4s</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">6s</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">BF</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #79aec8; color: white;">
                    <th style="padding: 8px; text-align: left;" colspan="8">Bowling Statistics</th>
                </tr>
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 8px; border: 1px solid #ddd;">O</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">M</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">R</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">W</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Avg</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Econ</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">SR</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">5W</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background-color: #79aec8; color: white;">
                    <th style="padding: 8px; text-align: left;" colspan="3">Fielding Statistics</th>
                </tr>
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 8px; border: 1px solid #ddd;">Catches</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Stumpings</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Run Outs</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                </tr>
            </table>
        </div>
        '''.format(
            # Batting stats
            batting.get('matches', 0),
            batting.get('innings', 0),
            batting.get('not_outs', 0),
            batting.get('runs', 0),
            batting.get('highest_score', 0),
            round(batting.get('average', 0), 2),
            round(batting.get('strike_rate', 0), 2),
            batting.get('fifties', 0),
            batting.get('hundreds', 0),
            batting.get('fours', 0),
            batting.get('sixes', 0),
            batting.get('balls', 0),
            # Bowling stats
            bowling.get('overs', 0),
            bowling.get('maidens', 0),
            bowling.get('runs', 0),
            bowling.get('wickets', 0),
            round(bowling.get('average', 0), 2),
            round(bowling.get('economy', 0), 2),
            round(bowling.get('strike_rate', 0), 2),
            bowling.get('five_wickets', 0),
            # Fielding stats
            fielding.get('catches', 0),
            fielding.get('stumpings', 0),
            fielding.get('runouts', 0)
        )
        return html

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
