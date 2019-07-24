from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import models
from django.db import transaction
# GeoDjango
from django.contrib.gis.geos import Point

from profiles.models import CustomUser, Profile
from activities.models import Activity


# FORMS FOR THE BACK OFFICE (ADMIN SITE)

class CustomUserCreationForm(UserCreationForm):
    '''
    A form that creates a basic user (CustomUser model), with no privileges, from the given
    email, username and password.
    '''
    email = models.EmailField()

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = CustomUser


# FORMS FOR THE FRONT OFFICE

class ProfileCreationForm(CustomUserCreationForm):
    '''
    A form that creates a profile (= CustomUser model with is_profile=True),
    with no privileges, from the given email, username and password.

    Also ask for a required list of activities (available in Activity model)
    and the availabilty area for practicing those activities.
    '''
    #error_css_class = 'contains_errors_as_ul_p'
    required_css_class = 'required'

    activities = forms.ModelMultipleChoiceField(
        label=_('Activities'),
        queryset=Activity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    availability_area = forms.CharField(
        label=_('Availability area'),
        help_text=_("Examples: 'Rhône-Alpes' or 'Around Grenoble, Chambéry, Lyon' or 'All the french Alpes'"),
        required=True
    )

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in filter(lambda item: item != 'activities', self.fields):
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
            if self.has_error('activities'):
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-invalid'})
            else:
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-valid'})
        else:
            for field in filter(lambda item: item != 'activities', self.fields):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline'})

    # class Meta(CustomUserForm.Meta):
    #     '''Defining the ordering of fields'''
    #     fields = ['username', 'email', 'password1', 'password2', 'activities', 'availability_area']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_profile = True
        user.save()
        profile = Profile.objects.create(user=user)
        profile.activities.add(*self.cleaned_data.get('activities'))
        profile.availability_area = self.cleaned_data.get('availability_area')
        profile.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )



class AccountForm(forms.ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in self.fields:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        else:
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )


class ProfileForm(forms.ModelForm):
    required_css_class = 'required'

    '''
    location = forms.CharField(
        label=_('Location'),
        max_length=200,
        help_text=_("Click on the map to show where you live."),
        required=False
    )
    '''

    availability_area_geo = forms.CharField(
        label=_('Availability area'),
        max_length=200,
        help_text=_("Click on the map to build the area where you are available for going out in the mountains."),
        required=False
    )

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in [f for f in self.fields if f not in ('public_profile', 'location', 'availability_area_geo', 'activities')]:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
            if self.has_error('activities'):
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-invalid'})
            else:
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-valid'})
        else:
            for field in [f for f in self.fields if f not in ('public_profile', 'location', 'availability_area_geo', 'activities')]:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields['public_profile'].widget.attrs.update({'class': 'custom-form-check-inline'})
            self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline'})

    class Meta:
        model = Profile
        fields = ['public_profile', 'profile_picture', 'location', 'availability_area_geo', 'availability_area', 'activities', 'introduction', 'list_of_courses', 'birthdate']
        widgets = {
            'activities': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        '''
        coordinates = self.cleaned_data.get('location').split(',')
        location = Point(float(coordinates[0]),float(coordinates[1]))
        '''
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )


class ContactProfileForm(forms.Form):
    required_css_class = 'required'

    from_email = forms.EmailField(label=_('Your e-mail address'), help_text=_("You will receive the contacted profile's answer on this e-mail."), required=True)
    subject = forms.CharField(label=_('Subject'), required=True)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea, required=True)

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in self.fields:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        else:
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        fields = ['from_email', 'subject', 'message']

    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )
