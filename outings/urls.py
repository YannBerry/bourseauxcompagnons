from django.utils.translation import gettext_lazy as _
from django.urls import path #, re_path

from outings.views import (
    OutingCreateView,
    OutingListView,
    OutingDetailView,
    OutingUpdateView,
    OutingDeleteView,
)

app_name = 'outings'
urlpatterns = [
    path('', OutingListView.as_view(), name='list'),
    path(_('create/'), OutingCreateView.as_view(), name='create'),
#    re_path(r'^search/$', OutingListView.as_view(), name='search'),
    path('<slug:slug>/', OutingDetailView.as_view(), name='detail'),
    path(_('<slug:slug>/edit/'), OutingUpdateView.as_view(), name='update'),
    path(_('<slug:slug>/delete/'), OutingDeleteView.as_view(), name='delete'),
]
