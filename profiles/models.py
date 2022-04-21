from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models #from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.admin import display
from bac.settings import LANGUAGES

from activities.models import Activity, Grade


class CustomUser(AbstractUser):
    """
    User model of bourseauxcompagnons.fr

    Customisation of the basic User Django model allowing
    to authenticate with {email + pwd} instead {username + pwd}.
    """
    email = models.EmailField(verbose_name=_('e-mail address'), unique=True)
    is_profile = models.BooleanField(verbose_name=_('profile status'), default=False)
    phone_number = PhoneNumberField(
        verbose_name=_('phone number'),
        help_text=_("Enter your phone number with your calling country code (Fr +33 | It +39 | Sp +34 | UK +44). Ex: write +33600000000 instead of 0600000000."),
        null=True,
        blank=True
    )
    language = models.CharField(
        verbose_name=_('language'),
        help_text=_("Language that will be used in the email we will send to you."),
        max_length=30,
        choices=LANGUAGES,
        default='fr'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('base user')
        verbose_name_plural = _('base users')

def user_directory_path_pict(instance, filename):
    ''' Return the path where to save a picture uploaded by a profile.'''
    username = instance.user.username
    date_added = f"{timezone.now().year}{timezone.now().month}{timezone.now().day}"
    time_added = f"{timezone.now().hour}{timezone.now().minute}{timezone.now().second}"
    return f"profiles/{username}/pictures/{date_added}_{time_added}-{username}-{filename}"


class Profile(models.Model):
    """
    Profile model of bourseauxcompagnons.fr

    onetoone relationship with CustomUser
    """
    # Attributes
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    public_profile = models.BooleanField(verbose_name=_('public profile'), default=True, help_text=_("When your profile is public, it is displayed in the profiles list."))
    location = models.PointField(
        verbose_name=_('location'),
        help_text=_("Click on the map to show where you live."),
        null=True,
        blank=True
    ) # default srid: 4326
    introduction = models.TextField(
        verbose_name=_('introduction'),
        help_text=_("Take your time to write a concise introduction that makes people want to know your better! The first 200 characters are displayed in the profiles list ;)"),
        blank=True
    )
    list_of_courses = models.TextField(verbose_name=_('list of courses'), blank=True)
    activities = models.ManyToManyField(
        Activity,
        verbose_name=_('activities'),
        help_text=_("Select at least one activity that you practice and for which you are searching for partners."),
        blank=False
    )
    grades = models.ManyToManyField(
        Grade,
        verbose_name=_('grades'),
        help_text=_("Select your comfortable grade for each of the activities you have chosen."),
        blank=True
    )
    availability_area_geo = models.PolygonField(
        verbose_name=_('availability area'),
        help_text=_("Click on the map to build the area where you are available for going out in the mountains. Tip: click on 'Shift' key while you draw to activate freehand drawing."),
        null=True,
        blank=True
    ) # default srid: 4326
    availability_area = models.CharField(
        verbose_name=_('availability area (further details)'),
        max_length=250,
        help_text=_("Examples: 'Rhône-Alpes' or 'Around Grenoble, Chambéry, Lyon' or 'All the french Alpes'."),
        null=True,
        blank=True
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
        '''Warning on ordering: if a groupby query (such as .annotate().values()) 
        is done on the model's META.ordering then this ordering will be ignored.
        In this case add a group_by() to the query to have the desired ordering.'''
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

    @display(boolean=True)
    def loggedin_less_than_12_month_ago(self):
        return self.user.last_login > timezone.now() - timedelta(weeks=52) if self.user.last_login else False

    @display(boolean=True)
    def updated_less_than_12_month_ago(self):
        return self.last_update > timezone.now() - timedelta(weeks=52)

    @property    
    def completion(self):
        weight = {
            'profile_picture': 15,
            'birthdate': 15,
            'introduction': 20,
            'location': 30,
            'availability_area_geo': 30,
            'availability_area': 5,
            'activities': 10,
            'grades': 20,
            'list_of_courses': 20
        }
        total_weight = sum(weight.values())
        completion_weight = 0
        if self.profile_picture:
            completion_weight += weight.get('profile_picture', 0)
        if self.birthdate:
            completion_weight += weight.get('birthdate', 0)
        if self.introduction:
            completion_weight += weight.get('introduction', 0)
        if self.location:
            completion_weight += weight.get('location', 0)
        if self.availability_area_geo:
            completion_weight += weight.get('availability_area_geo', 0)
        if self.availability_area:
            completion_weight += weight.get('availability_area', 0)
        if self.activities:
            completion_weight += weight.get('activities', 0)
        if self.grades:
            completion_weight += weight.get('grades', 0)
        if self.list_of_courses:
            completion_weight += weight.get('list_of_courses', 0)
        completion_percentage = round((completion_weight/total_weight)*100)
        return completion_percentage

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'username': self.user.username})
