from django.db import models
from django.utils.translation import gettext_lazy as _

from misc.db.models import CreateUpdateTracker


class Broadcast(models.Model, CreateUpdateTracker):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    text = models.TextField()
    tags = models.ManyToManyField('clients.Tag', related_name='broadcasts', blank=True, default=None)
    operators = models.ManyToManyField('clients.Operator', related_name='broadcasts', blank=True, default=None)

    class Meta:
        verbose_name = _('Broadcast')
        verbose_name_plural = _('broadcasts')

    def __str__(self):
        return self.text[:20] + '...'


class Message(models.Model, CreateUpdateTracker):
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    status_choices = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_SENT, _('Sent')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_CANCELLED, _('Cancelled')),
    )

    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='messages')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='messages')
    status = models.CharField(max_length=255, choices=status_choices, default=STATUS_PENDING)

    response = models.TextField(blank=True, default=None, null=True, editable=False)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return self.client.phone
