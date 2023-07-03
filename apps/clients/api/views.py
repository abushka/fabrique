from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from apps.clients.models import Client, Tag
from apps.clients.serializers.clients import ClientSerializer
from apps.clients.serializers.tags import TagSerializer



class ClientViewSet(ModelViewSet):
    model = Client
    queryset = model.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]



class TagViewSet(ModelViewSet):
    model = Tag
    queryset = model.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

