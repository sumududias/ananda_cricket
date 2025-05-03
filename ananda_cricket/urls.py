"""
URL configuration for ananda_cricket project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def redirect_to_admin(request):
    return redirect('admin:index')

urlpatterns = [
    path('', redirect_to_admin, name='index'),  # Redirect root to admin
    path('admin/', admin.site.urls),
    path('api/', include('cricket_stats.urls')),  # Changed from cricket_stats.api.urls
    path('api/auth/', include('rest_framework.urls')),  # For browsable API login
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# This serves media files during development ONLY
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
