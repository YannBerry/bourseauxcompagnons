from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model

from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.urls import reverse
from activities.models import Activity
from core.utils.slug import unique_slug_generator


class Availability(models.Model):
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    start_date = models.DateField(verbose_name=_('start'))
    end_date = models.DateField(verbose_name=_('end'))
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('author'))
    activities = models.ManyToManyField(Activity, blank=True, verbose_name=_('activities'))

    class Meta:
        verbose_name = _('availability')
        verbose_name_plural = _('availabilities')
        ordering = ['start_date']

    def __str__(self):
        return '{}-{} ({})'.format(self.start_date, self.end_date, self.author.username)
    
    @property
    def duration(self):
        delta = self.end_date - self.start_date
        duration = delta.days +1
        return duration

    def get_absolute_url(self):
        return reverse('availabilities:detail', kwargs={'slug': self.slug})


@receiver(pre_save, sender=Availability)
def slug_save(sender, instance, *args, **kwargs):
    ''' Function that fills out the slug field of a model with a unique slug'''
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, instance.start_date)