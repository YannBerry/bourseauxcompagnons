from django.views.generic import TemplateView
from datetime import date
from django.db.models import Q

from activities.models import Activity
from profiles.models import Profile
from outings.models import Outing


class HomepageView(TemplateView):
    template_name='index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['profiles'] = Profile.objects.filter(public_profile='True')
        context['5_last_profiles'] = Profile.objects.order_by('-user_id')[:6]
        context['5_last_outings'] = Outing.objects.filter(Q(start_date__gte=date.today()) | Q(end_date__gte=date.today())).order_by('-id')[:6]
        return context