from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save

from activities.models import Activity
from outings.utils import unique_slug_generator


class Outing(models.Model):
    title = models.CharField(
        verbose_name=_('title'),
        max_length=70,
        help_text=_("70 characters max.<br>Exemple: 'Meije Crossing - Normal route - Bivouac at the Grand Pic'.")
    )
    slug = models.SlugField(max_length=60, unique=True)
    description = models.TextField(
        verbose_name=_('description'),
        help_text=_("Take the time to write concise description that makes people want to join you!")
    )
    start_date = models.DateField(verbose_name=_('start'))
    end_date = models.DateField(verbose_name=_('end'))
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('authors'))
    activities = models.ManyToManyField(Activity, blank=False, verbose_name=_('activities'))
    topo_link = models.URLField(
        verbose_name=_("URL link to the outing topo"),
        blank=True,
        help_text=_("<a href='https://www.camptocamp.org/' target='_blank'>Camptocamp</a> and <a href='https://www.summitpost.org/' target='_blank'>SummitPost</a> are a high quality source of topos."),
    )
    #location = models.Charfield(max_length=200, blank=True)
    
    class Meta:
        verbose_name = _('outing')
        verbose_name_plural = _('outings')
        ordering = ['start_date']

    def __str__(self):
        return self.title

    @property
    def duration(self):
        delta = self.end_date - self.start_date
        duration = delta.days +1
        return duration
    
    def get_absolute_url(self):
        return reverse('outings:detail', kwargs={'slug': self.slug})


@receiver(pre_save, sender=Outing)
def slug_save(sender, instance, *args, **kwargs):
    ''' Function that fills out the slug field of a model with a unique slug'''
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, instance.title)
