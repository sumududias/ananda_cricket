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
    path('cricket_stats/', include('cricket_stats.urls')),  # Web views
    path('api/', include('cricket_stats.urls')),  # API views
    path('api/auth/', include('rest_framework.urls')),  # For browsable API login
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
