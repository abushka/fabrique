"""
URL configuration for notifications project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.settings import MEDIA_URL, MEDIA_ROOT, DEBUG
from docs.views import SpectacularRapiDocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('apps.clients.api.urls')),
    path('', include('apps.broadcasts.api.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularRapiDocView.as_view(url_name='schema'), name='docs'),
]

if DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(MEDIA_URL, document_root=MEDIA_ROOT)
