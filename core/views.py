from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from datetime import date
# Translation
from django.utils.translation import gettext_lazy as _

from activities.models import Activity
from profiles.models import Profile
from outings.models import Outing

from profiles.forms import ProfileAuthenticationForm, ProfilePasswordChangeForm, ProfilePasswordResetForm, ProfilePasswordResetConfirmForm


class HomepageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['profiles'] = Profile.objects.select_related('user').prefetch_related('activities').filter(public_profile='True', location__isnull=False)
        context['5_last_profiles'] = Profile.objects.select_related('user').prefetch_related('activities').order_by('-user_id')[:5]
        context['5_last_outings'] = Outing.objects.prefetch_related('activities').filter(start_date__gte=date.today()).order_by('-id')[:5]
        return context


class ProfileLoginView(SuccessMessageMixin, LoginView):
    authentication_form = ProfileAuthenticationForm


class ProfilePasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = ProfilePasswordChangeForm
    success_url = reverse_lazy('my-profile')
    success_message = _("Password changed! The next time you will sign in you will be able to use your new password!")


class ProfilePasswordResetView(SuccessMessageMixin, PasswordResetView):
    form_class = ProfilePasswordResetForm
    subject_template_name = 'registration/password_reset_subject.html'
    success_url = reverse_lazy('login')
    success_message = _("Password reset in progress. You've received an e-mail with a link to choose your new password. If you haven't received any e-mail, please check that you have filled the form out with the e-mail address you used to register and check your spam.")


class ProfilePasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = ProfilePasswordResetConfirmForm
    success_url = reverse_lazy('login')
    success_message = _("Your new password has been activated. You just have to sign in.")