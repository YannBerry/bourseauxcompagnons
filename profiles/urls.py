from django.utils.translation import gettext_lazy as _
from django.urls import path, re_path
from django.views.generic.base import TemplateView

from profiles.views import (
    ProfileListView,
    ProfileDetailView,
    ContactProfileView,
    export_profiles_to_xlsx,
)

app_name = 'profiles'
urlpatterns = [
    path('', ProfileListView.as_view(), name='list'),
    re_path(r'^search/$', ProfileListView.as_view(), name='search'),
    path('<username>/', ProfileDetailView.as_view(), name='detail'),
    path(_('<username>/contact/'), ContactProfileView, name='contact-profile'),
    path(_('<username>/contact/done/'), TemplateView.as_view(template_name='profiles/contact_profile_done.html'), name='contact-profile-done'),
    path(_('export/xlsx/'), export_profiles_to_xlsx, name='export-profiles-to-xlsx'),
]
