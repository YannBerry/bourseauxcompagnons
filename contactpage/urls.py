from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.views.generic.base import TemplateView

from contactpage.views import ContactPageView

app_name = 'contactpage'
urlpatterns = [
    path('', ContactPageView, name='contact-page'),
    path(_('email-sent/'), TemplateView.as_view(template_name='contactpage/contactpage_done.html'), name='email-sent'),
]
