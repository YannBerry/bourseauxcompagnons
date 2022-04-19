from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from core.mixins import UserPassesTestMixinNoPermissionDeny
# Messages
from django.contrib.messages.views import SuccessMessageMixin
# Translation
from django.utils.translation import gettext_lazy as _

from availabilities.models import Availability
from availabilities.forms import AvailabilityForm
from profiles.decorators import profile_required


class AvailabilityDetailView(DetailView):
    model = Availability


#VIEWS FOR AUTHENTICATED PROFILES

@method_decorator([login_required, profile_required], name='dispatch')
class AvailabilityCreateView(SuccessMessageMixin, CreateView):
    form_class = AvailabilityForm
    template_name = 'availabilities/availability_form.html'
    success_message = _("Your availability is now published! <a href='{}#cal-events'>Go back to my profile</a>")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message.format(reverse_lazy('my-profile'))


@method_decorator([login_required, profile_required], name='dispatch')
class AvailabilityUpdateView(UserPassesTestMixinNoPermissionDeny, SuccessMessageMixin, UpdateView):
    model = Availability
    form_class = AvailabilityForm
    success_message = _("Your availability is now updated! <a href='{}#cal-events'>Go back to my profile</a>")

    def test_func(self):
        availability_author = Availability.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == availability_author

    def get_success_message(self, cleaned_data):
        return self.success_message.format(reverse_lazy('my-profile'))


@method_decorator([login_required, profile_required], name='dispatch')
class AvailabilityDeleteView(UserPassesTestMixinNoPermissionDeny, DeleteView):
    model = Availability
    success_url = reverse_lazy('my-profile')

    def test_func(self):
        availability_author = Availability.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == availability_author
