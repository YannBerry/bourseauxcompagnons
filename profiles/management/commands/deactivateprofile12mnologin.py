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
    help = 'Deactivate the profile that did not connect to their account for more than 12 months + 1 week and inform them by email'

    def handle(self, *args, **options):
        profiles = Profile.objects.select_related('user').filter(Q(user__last_login__lt = timezone.now() - timedelta(weeks=53)) | Q(user__last_login = None))
        if profiles:
            subject=_("Warning before profile deactivation. Are you still using bourseauxcompagnons?")
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
                # Set the outdated profile to is_profile = False
                p.public_profile = False
                p.save(update_fields=['public_profile'])
            # Get the list of email adress of outdated profiles
            profileslist = ', '.join(str(p) for p in profiles)
            # Set the stdout display for the shell
            self.stdout.write(self.style.SUCCESS('Successfully deactivated the profiles that did not connect in the past 12 months + 1 week and informed them by email. Emails sent to: ' + profileslist))
        else:
            self.stdout.write(self.style.SUCCESS('All the profiles have at least 1 connection in the past 12 months + 1 week. No email sent.'))
