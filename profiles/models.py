from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models #from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
# Library for the function user_directory_path_pict
from django.utils import timezone
# Library to calculate the age of profile from its birthdate
from datetime import date
from django.contrib.auth.models import AbstractUser

from activities.models import Activity, Grade


class CustomUser(AbstractUser):
    """
    User model of bourseauxcompagnons.fr

    Customisation of the basic User Django model allowing
    to authenticate with {email + pwd} instead {username + pwd}.
    """
    email = models.EmailField(verbose_name=_('e-mail address'), unique=True)
    is_profile = models.BooleanField(verbose_name=_('profile status'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('base user')
        verbose_name_plural = _('base users')

def user_directory_path_pict(instance, filename):
    ''' Return the path where to save a picture uploaded by a profile.'''
    username = instance.user.username
    date_added = f"{timezone.now().year}{timezone.now().month}{timezone.now().day}"
    return f"profiles/{username}/pictures/{date_added}-{filename}"

class Profile(models.Model):
    """
    Profile model of bourseauxcompagnons.fr

    onetoone relationship with CustomUser
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    public_profile = models.BooleanField(verbose_name=_('public profile'), default=True, help_text=_("When your profile is public, it is displayed in the profiles list."))
    location = models.PointField(
        verbose_name=_('location'),
        help_text=_("Click on the map to show where you live."),
        null=True,
        blank=True)
    introduction = models.TextField(
        verbose_name=_('introduction'),
        help_text=_("Take your time to write a concise introduction that makes people want to know your better! The first 200 characters are displayed in the profiles list ;)"),
        blank=True
    )
    list_of_courses = models.TextField(verbose_name=_('list of courses'), blank=True)
    activities = models.ManyToManyField(Activity, blank=False, verbose_name=_('activities'))
    #grades = models.ManyToManyField(Grade, blank=True, verbose_name=_('grades'))
    availability_area_geo = models.PolygonField(
        verbose_name=_('availability area'),
        help_text=_("Click on the map to build the area where you are available for going out in the mountains."),
        null=True,
        blank=True
    )
    availability_area = models.CharField(
        verbose_name=_('availability area (further details)'),
        max_length=250,
        help_text=_("Examples: 'Rhône-Alpes' or 'Around Grenoble, Chambéry, Lyon' or 'All the french Alpes'.")
    )
    birthdate = models.DateField(
        verbose_name=_('birthdate'),
        help_text=_('Used to display your age on your public profile.'),
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(verbose_name = _('profile picture'), upload_to=user_directory_path_pict, null=True, blank=True)
    last_update = models.DateTimeField(verbose_name=_('last update'), auto_now=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ['-last_update']

    def __str__(self):
        return self.user.email

    @property    
    def age(self):
        if self.birthdate!=None:
            today = date.today()
            age = today.year - self.birthdate.year -((today.month, today.day)<(self.birthdate.month, self.birthdate.day))
        else:
            age = None
        return age

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'username': self.user.username})
