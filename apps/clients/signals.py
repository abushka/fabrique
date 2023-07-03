from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.clients.models import Client, Operator


@receiver(post_save, sender=Client)
def ensure_operator_exists(sender, instance, created, **kwargs):
    Operator.objects.get_or_create(code=instance.operator_code)
