from django.views.generic import TemplateView
from datetime import date
from django.urls import reverse_lazy

from activities.models import Activity
from profiles.models import Profile
from outings.models import Outing


class HomepageView(TemplateView):
    template_name='index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['profiles'] = Profile.objects.select_related('user').prefetch_related('activities').filter(public_profile='True', location__isnull=False)
        context['5_last_profiles'] = Profile.objects.select_related('user').prefetch_related('activities').order_by('-user_id')[:5]
        context['5_last_outings'] = Outing.objects.prefetch_related('activities').filter(start_date__gte=date.today()).order_by('-id')[:5]
        context['profiles_search_url'] = reverse_lazy('profiles:search')
        context['outings_search_url'] = reverse_lazy('outings:search')
        return context