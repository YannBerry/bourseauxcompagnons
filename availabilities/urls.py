from django.utils.translation import gettext_lazy as _
from django.urls import path

from availabilities.views import (
    AvailabilityCreateView,
    AvailabilityDetailView,
    AvailabilityUpdateView,
    AvailabilityDeleteView,
)

app_name = 'availabilities'
urlpatterns = [
    path(_('create/'), AvailabilityCreateView.as_view(), name='create'),
    path('<slug:slug>/', AvailabilityDetailView.as_view(), name='detail'),
    path(_('<slug:slug>/edit/'), AvailabilityUpdateView.as_view(), name='update'),
    path(_('<slug:slug>/delete/'), AvailabilityDeleteView.as_view(), name='delete'),
]
