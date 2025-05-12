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
    path('cricket_stats/', include('cricket_stats.urls', namespace='cricket_stats')),  # Include all cricket_stats URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Add media and static serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
