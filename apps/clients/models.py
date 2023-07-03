from django.db import models
from django.utils.translation import gettext_lazy as _

from misc.db.models import CreateUpdateTracker


def time_zone_choices():
    from pytz import common_timezones
    return [(tz, tz) for tz in common_timezones]


class Operator(models.Model, CreateUpdateTracker):
    code = models.CharField(max_length=3, unique=True, primary_key=True, verbose_name=_('code'))

    class Meta:
        verbose_name = _('Operator')
        verbose_name_plural = _('operators')

    def __str__(self):
        return self.code


class Tag(models.Model, CreateUpdateTracker):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, primary_key=True, verbose_name=_('slug'))

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        return super().save(*args, **kwargs)


class Client(models.Model, CreateUpdateTracker):
    phone = models.CharField(max_length=12)
    operator_code = models.CharField(max_length=3, editable=False)
    tags = models.ManyToManyField(Tag, related_name='clients')
    time_zone = models.CharField(max_length=255, choices=time_zone_choices(), null=True, blank=True, default=None)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('clients')

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if self.phone:
            self.operator_code = self.phone[1:4]
        return super().save(*args, **kwargs)
