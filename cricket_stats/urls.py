from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerViewSet,
    MatchViewSet,
    TeamViewSet,
    TournamentViewSet,
    MatchPlayerViewSet,
    SubstitutionViewSet,
    TeamStandingViewSet
)

router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'match-players', MatchPlayerViewSet)
router.register(r'substitutions', SubstitutionViewSet)
router.register(r'team-standings', TeamStandingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]