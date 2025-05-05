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
    player_profile
)

# API routes
router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'match-players', MatchPlayerViewSet)
router.register(r'substitutions', SubstitutionViewSet)
router.register(r'team-standings', TeamStandingViewSet)

# URL patterns
urlpatterns = [
    # API views
    path('', include(router.urls)),
    
    # Web views
    path('player/<int:player_id>/', player_profile, name='player_profile'),
]