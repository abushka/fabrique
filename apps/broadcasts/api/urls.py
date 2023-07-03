from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.broadcasts.api.views import BroadcastViewSet

router = DefaultRouter()

router.register(r'broadcasts', BroadcastViewSet, basename='broadcasts')

urlpatterns = [
    path('', include(router.urls)),
]
