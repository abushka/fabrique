from rest_framework import serializers

from apps.broadcasts.models import Broadcast


class BroadcastSerializer(serializers.ModelSerializer):

    class Meta:
        model = Broadcast
        fields = '__all__'
