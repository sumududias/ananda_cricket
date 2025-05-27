from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_admin
from . import views_dropdowns
from . import views_forms
from .views import (
    PlayerViewSet,
    TeamViewSet,
    TournamentViewSet,
    MatchViewSet,
    MatchPlayerViewSet,
    SubstitutionViewSet,
    TeamStandingViewSet,
    player_profile,
    player_list,
    PlayerDetailView,
    reports_dashboard,
    attendance_report,
    audit_report,
    match_scorecard,
    player_profile_report,
    match_list,
    team_performance_report,
    season_summary_report,
    batch_attendance_entry,
    training_session_list
)

app_name = 'cricket_stats'

# API routes
router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'match-players', MatchPlayerViewSet)
router.register(r'substitutions', SubstitutionViewSet)
router.register(r'team-standings', TeamStandingViewSet)

# Web view patterns
urlpatterns = [
    # Player URLs
    path('players/', player_list, name='player_list'),
    path('players/<int:player_id>/', player_profile, name='player_profile'),
    path('players/detail/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
    path('players/add/', views_forms.player_form, name='player_add'),
    path('players/edit/<int:player_id>/', views_forms.player_form, name='player_edit'),
    
    # Match URLs
    path('matches/', match_list, name='match_list'),
    path('matches/<int:match_id>/totals/', match_scorecard, name='match_totals'),
    path('matches/<int:match_id>/', match_scorecard, name='match_detail'),
    path('matches/add/', views_forms.match_form, name='match_add'),
    path('matches/edit/<int:match_id>/', views_forms.match_form, name='match_edit'),
    path('matches/<int:match_id>/players/add/', views_forms.match_player_form, name='match_player_add'),
    path('matches/<int:match_id>/players/<int:player_id>/edit/', views_forms.match_player_form, name='match_player_edit'),
    
    # Reports
    path('reports/', reports_dashboard, name='reports_dashboard'),
    path('reports/attendance/', attendance_report, name='attendance_report'),
    path('reports/audit/', audit_report, name='audit_report'),
    path('reports/match/<int:match_id>/', match_scorecard, name='match_scorecard'),
    path('reports/player/<int:player_id>/', player_profile_report, name='player_profile_report'),
    path('reports/team-performance/', team_performance_report, name='team_performance_report'),
    path('reports/season-summary/', season_summary_report, name='season_summary_report'),
    
    # Training Sessions and Attendance
    path('training-sessions/', training_session_list, name='training_session_list'),
    path('training-sessions/<int:session_id>/attendance/', batch_attendance_entry, name='batch_attendance_entry'),
    
    # API
    path('api/', include((router.urls, 'api'))),  # Add namespace to avoid conflicts
    
    # Admin views
    path('admin/backup-restore/', views_admin.backup_restore_view, name='backup_restore'),
    
    # Dropdown Management
    path('manage/bowling-styles/', views_dropdowns.manage_bowling_styles, name='manage_bowling_styles'),
    path('manage/batting-styles/', views_dropdowns.manage_batting_styles, name='manage_batting_styles'),
    path('manage/player-classes/', views_dropdowns.manage_player_classes, name='manage_player_classes'),
    path('manage/venues/', views_dropdowns.manage_venues, name='manage_venues'),
    path('manage/match-results/', views_dropdowns.manage_match_results, name='manage_match_results'),
    path('manage/dismissal-types/', views_dropdowns.manage_dismissal_types, name='manage_dismissal_types'),
    
    # AJAX Search Endpoints
    path('ajax/search/bowling-styles/', views_dropdowns.search_bowling_styles, name='search_bowling_styles'),
    path('ajax/search/batting-styles/', views_dropdowns.search_batting_styles, name='search_batting_styles'),
    path('ajax/search/player-classes/', views_dropdowns.search_player_classes, name='search_player_classes'),
    path('ajax/search/venues/', views_dropdowns.search_venues, name='search_venues'),
    path('ajax/search/match-results/', views_dropdowns.search_match_results, name='search_match_results'),
    path('ajax/search/dismissal-types/', views_dropdowns.search_dismissal_types, name='search_dismissal_types'),
    
    # AJAX Add Option
    path('ajax/add-dropdown-option/', views_dropdowns.add_dropdown_option, name='add_dropdown_option'),
]
