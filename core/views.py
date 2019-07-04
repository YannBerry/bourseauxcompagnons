from django.views.generic import TemplateView

from activities.models import Activity
from profiles.models import Profile
from outings.models import Outing


class HomepageView(TemplateView):
    template_name='index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['5_last_profiles'] = Profile.objects.order_by('-user_id')[:5]
        context['5_last_outings'] = Outing.objects.order_by('-id')[:5]
        return context