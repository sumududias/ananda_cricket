from django.urls import path, include
from cricket_stats import urls as cricket_urls

urlpatterns = [
    path('', include(cricket_urls)),
]