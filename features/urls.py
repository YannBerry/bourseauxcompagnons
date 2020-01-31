from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.views.generic.base import TemplateView

app_name = 'features'
urlpatterns = [
    path(_('votes/'), TemplateView.as_view(template_name="features/votes.html"), name='votes'),
    path(_('hoortus/'), TemplateView.as_view(template_name="features/hoortus.html"), name='hoortus'),
    path(_('hoortus/account'), TemplateView.as_view(template_name="features/account.html"), name='account'),
    path(_('hoortus/product'), TemplateView.as_view(template_name="features/product.html"), name='product'),
]
