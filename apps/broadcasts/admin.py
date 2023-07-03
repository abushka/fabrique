from django.contrib import admin

from apps.broadcasts.models import Broadcast, Message


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    filter_horizontal = ['tags', 'operators']

    class Meta:
        model = Broadcast


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('broadcast', 'client', 'response', 'created_at', 'updated_at')

    class Meta:
        model = Message
