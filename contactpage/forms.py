from django.utils.translation import gettext_lazy as _
from django import forms

from core.forms import NoColonForm


class ContactForm(NoColonForm):
    required_css_class = 'required'

    from_email = forms.EmailField(label=_('Your e-mail address'), required=True)
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
