from django.utils.translation import gettext_lazy as _
from django import forms

from availabilities.models import Availability

class AvailabilityForm(forms.ModelForm):
    #error_css_class = 'contains_errors_as_ul_p'
    required_css_class = 'required'

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

    class Meta:
        model = Availability
        fields = ['start_date', 'end_date', 'description', 'activities']
        widgets = {
            'activities': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Don't allow end_date < start_date.
        if start_date and end_date and end_date < start_date :
            self.add_error(
                'end_date',
                forms.ValidationError(
                    _("Your end date is not equal or later than your start date."),
                    code='chronology_error'
                )
            )
        if self.errors:
            self.add_error(
                None,
                forms.ValidationError(
                    _("Please correct detected error / errors.")
                )
            )
