from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.urls import path, include
#from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
# libraries for static
from django.conf import settings
from django.conf.urls.static import static

from core.views import HomepageView
from profiles.views import (
    ProfileRegisterView,
    ProfileHomepageView,
    ProfileUpdateView,
    AccountUpdateView,
    AccountDeleteView,
)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"), name="robots_file"),
]

urlpatterns += i18n_patterns(
    path('', HomepageView.as_view(), name='homepage'),
    path(_('accounts/'), include('django.contrib.auth.urls')),
    path(_('accounts/register/profile/'), ProfileRegisterView.as_view(), name='profile_register'),
    path(_('accounts/profiles/my-profile/'), ProfileHomepageView.as_view(), name='my-profile'),
    path(_('accounts/<username>/update/'), AccountUpdateView.as_view(), name='update-account'),
    path(_('accounts/profiles/<username>/update/'), ProfileUpdateView.as_view(), name='update-profile'),
    path(_('accounts/<username>/deletion/'), AccountDeleteView.as_view(), name='delete-account'),
    path(_('profiles/'), include('profiles.urls')),
    path(_('outings/'), include('outings.urls')),
    path(_('availabilities/'), include('availabilities.urls')),
    path(_('contact/'), include('contactpage.urls')),
    path(_('features/'), include('features.urls')),
    path(_('admin/'), admin.site.urls),
    #path(_('concept/'), TemplateView.as_view(template_name='concept/index.html'), name='concept'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
