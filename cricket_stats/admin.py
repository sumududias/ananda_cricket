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
        if obj and obj.format != 'TEST':
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
    list_display = ['match_date', 'team', 'opponent', 'format', 'result']
    list_filter = ['format', 'tournament', 'match_date']
    search_fields = ['team', 'opponent']
    date_hierarchy = 'match_date'

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('team', 'opponent'),
                ('match_date', 'venue'),
                ('match_type', 'format'),
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

    inlines = [MatchPlayerInline, SubstitutionInline]

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_photo', 'jersey_number', 'dob', 'primary_role']
    search_fields = ['first_name', 'last_name', 'jersey_number']
    list_filter = ['primary_role']
    readonly_fields = ['display_photo_large']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Personal Information', {
                'fields': ('first_name', 'last_name', 'dob', 'jersey_number', 'photo', 'display_photo_large')
            }),
            ('Cricket Information', {
                'fields': ('primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active')
            }),
        ]
        return fieldsets

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return format_html('<img src="/static/cricket_stats/default-player.png" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />')
    display_photo.short_description = 'Photo'

    def display_photo_large(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 8px;" />', obj.photo.url)
        return format_html('<img src="/static/cricket_stats/default-player.png" width="200" height="200" style="object-fit: cover; border-radius: 8px;" />')
    display_photo_large.short_description = 'Preview'

    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    name.admin_order_field = 'first_name'

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
    list_display = ('player', 'match', 'innings_number', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'innings_number', 'is_playing_xi')
    search_fields = ('player__first_name', 'player__last_name')

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
