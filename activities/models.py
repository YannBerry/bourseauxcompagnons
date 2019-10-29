from django.utils.translation import gettext_lazy as _
from django.db import models


class Activity(models.Model):
    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ['name']

    def __str__(self):
        return self.name


class Grade(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_('activity'))
    name = models.CharField(_('name'), max_length=50)
    
    class Meta:
        verbose_name = _('grade')
        verbose_name_plural = _('grades')

    def __str__(self):
        return f'{self.activity.name}: {self.name}'
