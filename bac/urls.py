from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.storage import staticfiles_storage
# libraries for static
from django.conf import settings
from django.conf.urls.static import static
# Translations
from django.utils.translation import gettext_lazy as _
# Sitemap
from django.contrib.sitemaps.views import sitemap
from bac.sitemaps import HomepageSitemap, ProfilesAndOutingsListsSitemap, ProfileSitemap, OutingSitemap, ContactPageSitemap
# Views
from django.contrib.auth import views as auth_views
from core.views import HomepageView, ProfileLoginView, ProfilePasswordChangeView, ProfilePasswordResetView, ProfilePasswordResetConfirmView
from profiles.views import (
    ProfileRegisterView,
    ProfileHomepageView,
    ProfileUpdateView,
    AccountUpdateView,
    AccountDeleteView,
)
#from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView


sitemaps = {
    'homepage': HomepageSitemap,
    'profiles_outings_lists': ProfilesAndOutingsListsSitemap,
    'profile_details': ProfileSitemap,
    'outing_details': OutingSitemap,
    'contact_page': ContactPageSitemap,
}

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))), # to have a https://bourseauxcompagnons.fr/favicon.ico URL in case browsers needs it on pages with no <link rel="icon" href=... For example my /robots.txt and /sitemap.xml
    path('robots.txt', lambda x: HttpResponse('User-Agent: *\nDisallow:\n\nSitemap: https://bourseauxcompagnons.fr/sitemap.xml', content_type='text/plain'), name='robots_file'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('', HomepageView.as_view(), name='homepage'),
    path(_('accounts/login/'), ProfileLoginView.as_view(), name='login'),
    path(_('accounts/logout/'), auth_views.LogoutView.as_view(), name='logout'),
    path(_('accounts/password-change/'), ProfilePasswordChangeView.as_view(), name='password_change'),
    path(_('accounts/password-reset/'), ProfilePasswordResetView.as_view(), name='password_reset'),
    path(_('accounts/reset/<uidb64>/<token>/'), ProfilePasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path(_('accounts/register/profile/'), ProfileRegisterView.as_view(), name='profile_register'),
    path(_('accounts/profiles/my-profile/'), ProfileHomepageView.as_view(), name='my-profile'),
    path(_('accounts/<username>/update/'), AccountUpdateView.as_view(), name='update-account'),
    path(_('accounts/profiles/<username>/update/'), ProfileUpdateView.as_view(), name='update-profile'),
    path(_('accounts/<username>/deletion/'), AccountDeleteView.as_view(), name='delete-account'),
    path(_('profiles/'), include('profiles.urls')),
    path(_('outings/'), include('outings.urls')),
    path(_('availabilities/'), include('availabilities.urls')),
    path(_('contact/'), include('contactpage.urls')),
    path(_('admin/'), admin.site.urls),
    #path(_('concept/'), TemplateView.as_view(template_name='concept/index.html'), name='concept'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
