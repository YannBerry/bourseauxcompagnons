from django.contrib.sitemaps import Sitemap
from django.urls import reverse
# Models for Sitemaps
from profiles.models import Profile
from outings.models import Outing


class i18nSitemap(Sitemap):
    i18n = True
    alternates = True


class HomepageSitemap(i18nSitemap):
    priority = 1
    changefreq = 'daily'
    x_default = True

    def items(self):
        return ['homepage',]

    def location(self, item):
        return reverse(item)


class ProfilesAndOutingsListsSitemap(i18nSitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['outings:list',
                'profiles:list',
                ]

    def location(self, item):
        return reverse(item)


class ProfileSitemap(i18nSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Profile.objects.filter()

    def lastmod(self, obj):
        return obj.last_update


class OutingSitemap(i18nSitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Outing.objects.filter()


class ContactPageSitemap(i18nSitemap):
    priority = 0.1
    changefreq = 'yearly'

    def items(self):
        return ['contactpage:contact-page',
                ]

    def location(self, item):
        return reverse(item)
