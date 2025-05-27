from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError
from django import forms
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import path
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
import subprocess
import os
import datetime
from .models import (
    Player, Match, MatchPlayer, MatchFormat, Team, Tournament, 
    Substitution, TeamStanding, TrainingSession, PlayerAttendance
)
from .models_choices import (
    BOWLING_STYLE_CHOICES, BATTING_STYLE_CHOICES, PLAYER_CLASS_CHOICES,
    VENUE_CHOICES, MATCH_RESULT_CHOICES, DISMISSAL_TYPE_CHOICES
)

# Custom Admin Site with backup functionality
class CricketAdminSite(AdminSite):
    site_header = "Ananda College Cricket Statistics Administration"
    site_title = "Ananda Cricket Admin"
    index_title = "Cricket Statistics Management"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('backup_database/', self.admin_view(self.backup_database), name='backup_database'),
        ]
        return custom_urls + urls
    
    def backup_database(self, request):
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'ananda_cricket_backup_{timestamp}.sql')
        
        # Get database settings from settings.py
        from django.conf import settings
        db_settings = settings.DATABASES['default']
        
        if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            # SQLite backup
            import shutil
            shutil.copy2(db_settings['NAME'], backup_file + '.sqlite3')
            message = f'SQLite database backup created at {backup_file}.sqlite3'
        elif db_settings['ENGINE'] == 'django.db.backends.mysql':
            # MySQL backup
            cmd = [
                'mysqldump',
                '-u', db_settings['USER'],
                f"--password={db_settings['PASSWORD']}",
                '-h', db_settings.get('HOST', 'localhost'),
                '--databases', db_settings['NAME'],
                '-r', backup_file
            ]
            try:
                subprocess.run(cmd, check=True)
                message = f'MySQL database backup created at {backup_file}'
            except subprocess.CalledProcessError as e:
                return HttpResponse(f'Error creating backup: {str(e)}', status=500)
        else:
            return HttpResponse('Unsupported database engine', status=400)
        
        # Return success message
        return HttpResponse(f'<h1>Database Backup</h1><p>{message}</p><p><a href="/admin/">Return to admin</a></p>')

# Create custom admin site instance
cricket_admin_site = CricketAdminSite(name='cricket_admin')

# Register the models with our custom admin site
# Note: We'll use the custom site for rendering but still register with the default site
# for compatibility with existing code
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
    fieldsets = (
        (None, {
            'fields': ('player', 'innings_number', 'batting_order', 'is_playing_xi', 'is_captain', 'is_keeper', 'comments')
        }),
        ('Batting', {
            'fields': ('runs_scored', 'balls_faced', 'fours', 'sixes', 'how_out'),
            'classes': ('collapse',)
        }),
        ('Bowling', {
            'fields': ('overs_bowled', 'maidens_bowled', 'runs_conceded', 'wickets_taken', 'wides', 'no_balls'),
            'classes': ('collapse',)
        }),
        ('Fielding', {
            'fields': ('catches', 'run_outs', 'stumpings', 'direct_hits', 'dropped_catches'),
            'classes': ('collapse',)
        }),
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and hasattr(obj, 'format') and obj.format and not obj.format.is_limited_overs:
            formset.form.base_fields['innings_number'].widget.choices = [
                (1, '1st Innings'),
                (2, '2nd Innings'),
            ]
        else:
            formset.form.base_fields['innings_number'].widget.choices = [
                (1, '1st Innings'),
            ]
        return formset

    def save_formset(self, request, form, formset, change):
        if formset.model == MatchPlayer:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk and not instance.innings_number:
                    instance.innings_number = 1
                instance.save()
            formset.save_m2m()
        else:
            formset.save()

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 1
    fields = ['player_out', 'player_in', 'reason', 'substitution_time', 'comments']

class PlayerResource(resources.ModelResource):
    class Meta:
        model = Player
        import_id_fields = ['id']
        fields = ('id', 'first_name', 'last_name', 'dob', 'jersey_number', 'primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active')

class TeamResource(resources.ModelResource):
    class Meta:
        model = Team
        import_id_fields = ['id']

class TournamentResource(resources.ModelResource):
    class Meta:
        model = Tournament
        import_id_fields = ['id']

class MatchResource(resources.ModelResource):
    class Meta:
        model = Match
        import_id_fields = ['id']

class MatchPlayerResource(resources.ModelResource):
    class Meta:
        model = MatchPlayer
        import_id_fields = ['id']

class SubstitutionResource(resources.ModelResource):
    class Meta:
        model = Substitution
        import_id_fields = ['id']

class TeamStandingResource(resources.ModelResource):
    class Meta:
        model = TeamStanding
        import_id_fields = ['id']

class MatchFormatResource(resources.ModelResource):
    class Meta:
        model = MatchFormat
        import_id_fields = ['id']

class TrainingSessionResource(resources.ModelResource):
    class Meta:
        model = TrainingSession
        import_id_fields = ['id']

class PlayerAttendanceResource(resources.ModelResource):
    class Meta:
        model = PlayerAttendance
        import_id_fields = ['id']

@admin.register(Match)
class MatchAdmin(ImportExportModelAdmin):
    resource_class = MatchResource
    list_display = ['__str__', 'match_date', 'college_name', 'get_team', 'get_opponent', 'get_format', 'result']
    list_filter = ['format__name', 'tournament__name', 'match_date']
    search_fields = ['college_name', 'opponent', 'team__name']  # Updated search fields
    date_hierarchy = 'match_date'
    inlines = [MatchPlayerInline, SubstitutionInline]
    
    class Media:
        css = {
            'all': ('cricket_stats/css/admin_custom.css',)
        }
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('college_name', 'team'),
                 ('opponent', 'match_date'),
                ('venue', 'format', 'match_days'),
                'tournament'
            )
        }),
        ('Match Result', {
            'fields': ('result', 'man_of_match', 'toss_winner', 'toss_decision'),
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

    def get_team(self, obj):
        try:
            if obj.team and hasattr(obj.team, 'name'):
                return obj.team.name
            elif obj.team_name:
                return obj.team_name
            else:
                return "No Team Selected"
        except (ValueError, AttributeError, TypeError):
            return obj.team_name if obj.team_name else "No Team Selected"
    get_team.short_description = 'Team'
    get_team.admin_order_field = 'team__name'

    def get_opponent(self, obj):
        return obj.opponent
    get_opponent.short_description = 'Opponent'
    get_opponent.admin_order_field = 'opponent'

    def get_format(self, obj):
        return obj.format.name if obj.format else None
    get_format.short_description = 'Format'
    get_format.admin_order_field = 'format__name'

@admin.register(Player)
class PlayerAdmin(ImportExportModelAdmin):
    resource_class = PlayerResource
    list_display = ['name', 'display_photo', 'jersey_number', 'dob', 'primary_role']
    search_fields = ['first_name', 'last_name', 'jersey_number']
    list_filter = ['primary_role']
    readonly_fields = ['display_photo_large']
    
    def get_fieldsets(self, request, obj=None):
        return [
            ('Personal Information', {
                'fields': ('first_name', 'last_name', 'dob', 'jersey_number', 'photo', 'display_photo_large')
            }),
            ('Cricket Information', {
                'fields': ('primary_role', 'batting_style', 'bowling_style', 'player_class', 'year_joined', 'is_active')
            }),
        ]

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

@admin.register(Team)
class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    list_display = ('name', 'season', 'captain')
    search_fields = ('name',)

@admin.register(Tournament)
class TournamentAdmin(ImportExportModelAdmin):
    resource_class = TournamentResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MatchPlayer)
class MatchPlayerAdmin(ImportExportModelAdmin):
    resource_class = MatchPlayerResource
    list_display = ('player', 'match', 'innings_number', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'innings_number', 'is_playing_xi')
    search_fields = ('player__first_name', 'player__last_name')

@admin.register(Substitution)
class SubstitutionAdmin(ImportExportModelAdmin):
    resource_class = SubstitutionResource
    list_display = ('match', 'player_out', 'player_in', 'substitution_time')
    list_filter = ('match',)
    search_fields = ('player_out__first_name', 'player_out__last_name', 'player_in__first_name', 'player_in__last_name')

@admin.register(TeamStanding)
class TeamStandingAdmin(ImportExportModelAdmin):
    resource_class = TeamStandingResource
    list_display = ('tournament', 'team', 'matches_played', 'matches_won', 'matches_lost', 'points', 'position')
    list_filter = ('tournament', 'team')
    search_fields = ('team__name', 'tournament__name')

@admin.register(MatchFormat)
class MatchFormatAdmin(ImportExportModelAdmin):
    resource_class = MatchFormatResource
    list_display = ('name', 'short_name', 'is_limited_overs', 'is_practice', 'is_active')
    list_filter = ('is_limited_overs', 'is_practice', 'is_active')
    search_fields = ('name', 'short_name')
    fields = ('name', 'short_name', 'is_limited_overs', 'is_practice', 'is_active')

class TrainingSessionAdmin(ImportExportModelAdmin):
    resource_class = TrainingSessionResource
    """Admin view for training sessions"""
    list_display = ('__str__', 'session_type', 'date', 'start_time', 'end_time')
    list_filter = ('session_type', 'date')
    search_fields = ('notes',)
    date_hierarchy = 'date'
    ordering = ('-date', '-start_time')
    
    fieldsets = (
        ('Session Details', {
            'fields': ('session_type', 'date', 'start_time', 'end_time', 'notes')
        }),
    )

# Register the TrainingSession model with the admin site
admin.site.register(TrainingSession, TrainingSessionAdmin)

# Register our custom attendance management model
class AttendanceManagement(TrainingSession):
    class Meta:
        proxy = True
        verbose_name = 'Attendance Management'
        verbose_name_plural = 'Attendance Management'

# Don't register the custom attendance management to avoid duplicates
# admin.site.register(AttendanceManagement, AttendanceAdmin)

# Register models with the custom admin site for the backup functionality
cricket_admin_site.register(Player, PlayerAdmin)
cricket_admin_site.register(Team, TeamAdmin)
cricket_admin_site.register(Tournament, TournamentAdmin)
cricket_admin_site.register(Match, MatchAdmin)
cricket_admin_site.register(MatchPlayer, MatchPlayerAdmin)
cricket_admin_site.register(Substitution, SubstitutionAdmin)
cricket_admin_site.register(TeamStanding, TeamStandingAdmin)
cricket_admin_site.register(MatchFormat, MatchFormatAdmin)
cricket_admin_site.register(TrainingSession, TrainingSessionAdmin)

# Add a template tag to display the backup button in the admin index
from django.templatetags.static import static
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.urls import reverse

# Add a custom template tag to include the backup button
admin.site.index_template = 'admin/custom_admin_index.html'