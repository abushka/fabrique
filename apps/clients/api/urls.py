from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clients.api.views import ClientViewSet, TagViewSet

router = DefaultRouter()

router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
