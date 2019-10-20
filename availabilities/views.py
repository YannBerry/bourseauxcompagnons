from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin

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
    success_message = "Votre disponibilité est désormais publiée !"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@method_decorator([login_required, profile_required], name='dispatch')
class AvailabilityUpdateView(UserPassesTestMixin, UpdateView):
    model = Availability
    form_class = AvailabilityForm

    def test_func(self):
        availability_author = Availability.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == availability_author


@method_decorator([login_required, profile_required], name='dispatch')
class AvailabilityDeleteView(UserPassesTestMixin, DeleteView):
    model = Availability
    success_url = reverse_lazy('my-profile')

    def test_func(self):
        availability_author = Availability.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == availability_author
