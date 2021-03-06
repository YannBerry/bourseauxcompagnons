from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.views.generic.base import TemplateView

app_name = 'features'
urlpatterns = [
    path(_('votes/'), TemplateView.as_view(template_name="features/votes.html"), name='votes'),
]
