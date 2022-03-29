from django.utils.translation import gettext_lazy as _
from django.db import models


class Activity(models.Model):
    name = models.CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        '''Warning on ordering: if a groupby query (such as .annotate().values()) 
        is done on the model's META.ordering then this ordering will be ignored.
        In this case add a group_by() to the query to have the desired ordering.'''
        ordering = ['name']

    def __str__(self):
        return self.name


class Grade(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_('activity'))
    name = models.CharField(_('name'), max_length=50)
    ordering = models.PositiveIntegerField(_('ordering'))
    
    class Meta:
        verbose_name = _('grade')
        verbose_name_plural = _('grades')
        ordering = ['activity__name', 'ordering']

    def __str__(self):
        return self.name
        # return f'{self.activity.name}: {self.name}'
