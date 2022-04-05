from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.views.generic.base import TemplateView

from contactpage.views import ContactPageView

app_name = 'contactpage'
urlpatterns = [
    path('', ContactPageView, name='contact-page'),
]
