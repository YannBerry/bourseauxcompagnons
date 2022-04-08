from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import models
from django.db import transaction
from django.db.models import Q
# GEODJANGO
from django.contrib.gis.forms.fields import PolygonField as FormPolygonField
from core.widgets import OpenLayersWidgetSrid4326
# from django.contrib.gis.geos import Point
# DJANGO-PHONENUMBER-FIELD
# from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.widgets import PhoneNumberPrefixWidget

# MODELS
from profiles.models import CustomUser, Profile
from activities.models import Activity, Grade
# FORMS
from core.forms import NoColonForm, NoColonModelForm, GroupedModelMultipleChoiceField
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
# WIDGETS
from core.widgets import ImageWidget, GradesWidget, SelectableItemsWidget, ToggleSwitchWidget


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

class ProfileCreationForm(NoColonForm, CustomUserCreationForm):
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
        widget=SelectableItemsWidget(),
    )

    availability_area_geo = FormPolygonField(
        label=_('Availability area'),
        help_text=_("Click on the map to build the area where you are available for going out in the mountains."),
        widget=OpenLayersWidgetSrid4326(),
    )

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in [f for f in self.fields if f not in ('availability_area_geo', 'activities')]:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
            if self.has_error('activities'):
                self.fields['activities'].widget.attrs.update({'class': 'p-1 rounded is-invalid'})
            else:
                self.fields['activities'].widget.attrs.update({'class': 'p-1 rounded is-valid'})
        else:
            for field in [f for f in self.fields if f not in ('availability_area_geo', 'activities')]:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    # class Meta(CustomUserForm.Meta):
        # '''Defining the ordering of fields'''
        # fields = ['email', 'username', 'password1', 'password2', 'activities', 'availability_area_geo']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_profile = True
        user.save()
        profile = Profile.objects.create(user=user)
        profile.activities.add(*self.cleaned_data.get('activities'))
        profile.availability_area_geo = self.cleaned_data.get('availability_area_geo')
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


class ProfileAuthenticationForm(NoColonForm, AuthenticationForm):
    required_css_class = 'required'


    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        for field in [f for f in self.fields]:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )

class ProfilePasswordChangeForm(NoColonForm, PasswordChangeForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in [f for f in self.fields]:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        else:
            for field in [f for f in self.fields]:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )


class ProfilePasswordResetForm(NoColonForm, PasswordResetForm):
    required_css_class = 'required'
    
    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for field in [f for f in self.fields]:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
        else:
            for field in [f for f in self.fields]:
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class AccountForm(NoColonModelForm):
    required_css_class = 'required'

    # phone_number = PhoneNumberField(
    #     label=_('Phone number'),
    #     widget= PhoneNumberPrefixWidget(),
    #     required=False
    # )

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
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )


class ProfileForm(NoColonModelForm):
    required_css_class = 'required'

    grades = GroupedModelMultipleChoiceField(
        queryset=Grade.objects.all(),
        label=_('Grades'),
        choices_groupby='activity',
        widget= GradesWidget(), #forms.CheckboxSelectMultiple(),
        required=False,
        help_text=_("Select your comfortable grade for each of the activities you have chosen.")
    )

    def __init__(self, *args, **kwargs):
        '''Inherit from parent and add the Bootstrap form-control class to the fields'''
        super().__init__(*args, **kwargs)
        # CSS styles
        if self.is_bound:
            for field in [f for f in self.fields if f not in ('public_profile', 'profile_picture', 'location', 'availability_area_geo', 'activities', 'grades')]:
                if self.has_error(field):
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-valid'})
            if self.has_error('activities'):
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-invalid'})
            else:
                self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline is-valid'})
            if self.has_error('grades'):
                self.fields['grades'].widget.attrs.update({'class': 'custom-form-check-inline is-invalid'})
            else:
                self.fields['grades'].widget.attrs.update({'class': 'custom-form-check-inline is-valid'})
        else:
            for field in [f for f in self.fields if f not in ('public_profile', 'profile_picture', 'location', 'availability_area_geo', 'activities', 'grades')]:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields['profile_picture'].widget.attrs.update({'class': 'custom-file-input'})
            self.fields['activities'].widget.attrs.update({'class': 'custom-form-check-inline'})
            self.fields['grades'].widget.attrs.update({'class': 'custom-form-check-inline'})
        self.fields['public_profile'].widget.label = self.fields['public_profile'].label
        # Dependent lists: grades displaying according to selected activities
        # self.fields['grades'].queryset = Grade.objects.none()
        if self.instance.pk:
            activities = self.instance.activities.all()
            # q = Grade.objects.none()
            # for a in self.instance.activities.all():
            #     q |= a.grade_set.all()
            # print(q)
            self.fields['grades'].queryset = Grade.objects.select_related('activity').filter(eval(' | '.join(f'Q(activity="{ activity.pk }")' for activity in activities)))

    class Meta:
        model = Profile
        fields = ['public_profile', 'profile_picture', 'location', 'availability_area_geo', 'availability_area', 'activities', 'grades', 'introduction', 'list_of_courses', 'birthdate']
        widgets = {
            'public_profile': ToggleSwitchWidget(),
            'location': OpenLayersWidgetSrid4326(),
            'availability_area_geo': OpenLayersWidgetSrid4326(),
            'profile_picture': ImageWidget(),
            'activities': SelectableItemsWidget(),
        }

    def clean(self):
        cleaned_data = super().clean()
        # coordinates = self.cleaned_data.get('location').split(',')
        # print(coordinates[0])
        # print(coordinates[1])
        # location = Point(float(coordinates[0]),float(coordinates[1]))
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )


class ContactProfileForm(NoColonForm):
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
