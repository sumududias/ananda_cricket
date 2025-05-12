from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerViewSet,
    TeamViewSet,
    TournamentViewSet,
    MatchViewSet,
    MatchPlayerViewSet,
    SubstitutionViewSet,
    TeamStandingViewSet,
    player_profile,
    player_list
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

# Web view patterns - removed 'web/' prefix
web_urlpatterns = [
    path('players/', player_list, name='player_list'),
    path('players/<int:player_id>/', player_profile, name='player_profile'),
]

# API URL patterns - moved under /cricket_stats/api/
api_urlpatterns = [
    path('api/', include((router.urls, 'api'))),  # Add namespace to avoid conflicts
]

# Combined patterns
urlpatterns = web_urlpatterns + api_urlpatterns