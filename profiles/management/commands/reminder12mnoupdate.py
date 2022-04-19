from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
# Translations
from django.utils.translation import gettext_lazy as _
# Sites
from django.contrib.sites.models import Site
# Sending Emails
from django.core.mail import BadHeaderError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q

from profiles.models import Profile


class Command(BaseCommand):
    help = 'Send an email to profiles that did not connect to their account in the past 12 months'

    def handle(self, *args, **options):
        profiles = Profile.objects.select_related('user').filter(last_update__lt = timezone.now() - timedelta(weeks=52))
        if profiles:
            subject=_("Think to update your profile!")
            subject_prefixed = _("[Account] {}").format(subject)
            from_email = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
            for p in profiles:
                # Send Warning email to outdated profiles
                recipients = [p.user.email]
                current_site = Site.objects.get_current()
                email_context = {'customuser': p.user,
                                'site_name': current_site.name,
                                'domain': current_site.domain,
                                'protocol': "https"
                }
                #html_message = render_to_string('profiles/profile_register_email_inline.html', email_context)
                plain_message = render_to_string('profiles/profile_register_email_plain.html', email_context)
                try:
                    send_mail(subject_prefixed, plain_message, from_email, recipients)#, html_message=html_message)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            # Get the list of email adress of outdated profiles
            profileslist = ', '.join(str(p) for p in profiles)
            # Set the stdout display for the shell
            self.stdout.write(self.style.SUCCESS('Successfully sent an email to profiles that did not connect in the past 12 months. Emails sent to: ' + profileslist))
        else:
            self.stdout.write(self.style.SUCCESS('All the profiles have at least 1 connection in the past 12 months. No email sent.'))
