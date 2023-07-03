from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.db.models import Count

from apps.broadcasts.models import Broadcast, Message
from apps.broadcasts.serializers.broadcasts import BroadcastSerializer
from apps.broadcasts.serializers.messages import MessageSerializer


class BroadcastViewSet(ModelViewSet):
    model = Broadcast
    queryset = model.objects.all()
    serializer_class = BroadcastSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @action(methods=['get'], detail=True, url_path='stats_short')
    def stats_short(self, request, pk=None):
        """
        Возвращает краткую статистику по рассылкам.
        """
        total_broadcasts = Broadcast.objects.count()
        total_messages = Message.objects.values('status').annotate(count=Count('status'))

        response_data = {
            'total_broadcasts': total_broadcasts,
            'total_messages': total_messages
        }
        return Response(response_data)

    @action(methods=['get'], detail=True, url_path='stats_full')
    def stats_full(self, request, pk=None):
        """
        Возвращает полную статистику по рассылке.
        """
        broadcast = self.get_object()
        total_messages = broadcast.messages.count()
        message_statistics = broadcast.messages.values('status').annotate(count=Count('status'))
        messages = Message.objects.filter(broadcast=pk)
        serializer = MessageSerializer(messages, many=True)

        response_data = {
            'total_messages': total_messages,
            'message_statistics': message_statistics,
            'messages': serializer.data
        }
        return Response(response_data)
