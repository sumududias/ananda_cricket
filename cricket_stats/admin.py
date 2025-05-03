from django.contrib import admin
from .models import Player, Match, Team, MatchPlayer, Substitution, Tournament, TeamStanding
from django.utils.safestring import mark_safe
from django.utils.html import format_html

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'primary_role', 'batting_stats_display', 'bowling_stats_display', 'fielding_stats_display')
    list_display_links = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    list_filter = ('primary_role', 'is_active')
    
    readonly_fields = (
        'batting_stats_display', 'bowling_stats_display', 'fielding_stats_display'
    )

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'dob', 'photo', 'is_active')
        }),
        ('Cricket Information', {
            'fields': ('batting_style', 'bowling_style', 'primary_role', 'player_class', 'year_joined')
        }),
        ('Statistics', {
            'fields': (
                'batting_stats_display',
                'bowling_stats_display',
                'fielding_stats_display'
            ),
            'classes': ('wide',)
        })
    )

    def batting_stats_display(self, obj):
        try:
            stats = obj.batting_stats
            print(f"DEBUG - Batting stats: {stats}")
            
            # Pre-format the decimal values
            avg = "{:.2f}".format(float(stats['average']))
            sr = "{:.2f}".format(float(stats['strike_rate']))
            
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="4" style="text-align:left; padding:5px; background-color:#f5f5f5">Batting Statistics</th></tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Matches:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Innings:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Not Outs:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Highest:</b> {}</td>'
                '</tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Runs:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Balls:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>4s/6s:</b> {}/{}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Avg/SR:</b> {}/{}</td>'
                '</tr>'
                '</table>',
                stats['matches'],
                stats['innings'],
                stats['not_outs'],
                stats['highest_score'],
                stats['runs'],
                stats['balls_faced'],
                stats['fours'],
                stats['sixes'],
                avg,
                sr
            )
        except Exception as e:
            print(f"DEBUG - Error in batting_stats_display: {str(e)}")
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="4" style="text-align:left; padding:5px; background-color:#f5f5f5">Batting Statistics</th></tr>'
                '<tr><td colspan="4" style="padding:5px; border:1px solid #ddd">No batting statistics available</td></tr>'
                '</table>'
            )
    batting_stats_display.short_description = 'Batting'

    def bowling_stats_display(self, obj):
        try:
            stats = obj.bowling_stats
            print(f"DEBUG - Bowling stats: {stats}")
            
            # Pre-format the decimal values
            avg = "{:.2f}".format(float(stats['average']))
            econ = "{:.2f}".format(float(stats['economy']))
            sr = "{:.2f}".format(float(stats['strike_rate']))
            
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="4" style="text-align:left; padding:5px; background-color:#f5f5f5">Bowling Statistics</th></tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Matches:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Innings:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Overs:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Best:</b> {}</td>'
                '</tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Wickets:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Runs:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Avg:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Econ/SR:</b> {}/{}</td>'
                '</tr>'
                '</table>',
                stats['matches'],
                stats['innings'],
                stats['overs'],
                stats['best_bowling'],
                stats['wickets'],
                stats['runs'],
                avg,
                econ,
                sr
            )
        except Exception as e:
            print(f"DEBUG - Error in bowling_stats_display: {str(e)}")
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="4" style="text-align:left; padding:5px; background-color:#f5f5f5">Bowling Statistics</th></tr>'
                '<tr><td colspan="4" style="padding:5px; border:1px solid #ddd">No bowling statistics available</td></tr>'
                '</table>'
            )
    bowling_stats_display.short_description = 'Bowling'

    def fielding_stats_display(self, obj):
        try:
            stats = obj.fielding_stats
            print(f"DEBUG - Fielding stats: {stats}")
            total = int(stats['catches']) + int(stats['stumpings']) + int(stats['runouts'])
            
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="3" style="text-align:left; padding:5px; background-color:#f5f5f5">Fielding Statistics</th></tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Matches:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Innings:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Total:</b> {}</td>'
                '</tr>'
                '<tr>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Catches:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Stumpings:</b> {}</td>'
                '<td style="padding:5px; border:1px solid #ddd"><b>Run Outs:</b> {}</td>'
                '</tr>'
                '</table>',
                stats['matches'],
                stats.get('innings', 0),
                total,
                stats['catches'],
                stats['stumpings'],
                stats['runouts']
            )
        except Exception as e:
            print(f"DEBUG - Error in fielding_stats_display: {str(e)}")
            return format_html(
                '<table style="width:100%; border-collapse:collapse">'
                '<tr><th colspan="3" style="text-align:left; padding:5px; background-color:#f5f5f5">Fielding Statistics</th></tr>'
                '<tr><td colspan="3" style="padding:5px; border:1px solid #ddd">No fielding statistics available</td></tr>'
                '</table>'
            )
    fielding_stats_display.short_description = 'Fielding'

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    extra = 11  # Show 11 empty forms for a cricket team
    fields = ('player', 'batting_order', 'runs_scored', 'balls_faced', 'fours', 'sixes', 
             'how_out', 'overs_bowled', 'runs_conceded', 'wickets_taken', 'catches', 
             'stumpings', 'runouts', 'is_playing_xi', 'is_substitute')

class SubstitutionInline(admin.TabularInline):
    model = Substitution
    extra = 1

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'opponent', 'result')
    list_filter = ('match_type', 'result')
    search_fields = ('opponent', 'tournament__name')
    inlines = [MatchPlayerInline, SubstitutionInline]  # Add player details inline

    fieldsets = (
        ('Match Details', {
            'fields': ('team', 'opponent', 'date', 'venue', 'match_type', 'tournament')
        }),
        ('Toss Information', {
            'fields': ('toss_winner', 'toss_decision')
        }),
        ('Match Result', {
            'fields': ('result', 'ananda_score', 'opponent_score', 'man_of_match')
        }),
        ('Additional Information', {
            'fields': ('summary', 'scorecard_photo')
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'coach')
    search_fields = ('name', 'coach')

def scorecard_preview(self, obj):
    if obj.scorecard_photo:
        return mark_safe(f'<img src="{obj.scorecard_photo.url}" width="300" />')
    return "No photo uploaded"

scorecard_preview.short_description = 'Scorecard Preview'

@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ('match', 'player', 'runs_scored', 'wickets_taken')
    list_filter = ('match', 'player')

@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ('match', 'player_out', 'player_in', 'reason')
    list_filter = ('match', 'reason')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'start_date', 'end_date')
    search_fields = ('name', 'organizer')

@admin.register(TeamStanding)
class TeamStandingAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'team', 'matches_played', 'points', 'position')
    list_filter = ('tournament', 'team')
