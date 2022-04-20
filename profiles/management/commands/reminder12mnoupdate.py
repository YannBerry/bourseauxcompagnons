from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
# Translations
from django.utils.translation import gettext_lazy as _
from django.utils import translation
# Sites
from django.contrib.sites.models import Site
# Sending Emails
from django.core.mail import BadHeaderError, EmailMultiAlternatives

from profiles.models import Profile


class Command(BaseCommand):
    help = 'Send a reminder email to profiles that did not update their account in the past 12 months'

    def handle(self, *args, **options):
        profiles = Profile.objects.select_related('user').filter(last_update__lt = timezone.now() - timedelta(weeks=52))
        if profiles:
            translation.activate('fr')
            current_site = Site.objects.get_current()
            subject=_("Think to update your profile!")
            subject_prefixed = _("[Account] {}").format(subject)
            from_email = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
            bcc_bac = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
            for p in profiles:
                # Send reminder email to outdated profiles
                recipients = [p.user.email]
                email_context = {'customuser': p.user,
                                'site_name': current_site.name,
                                'domain': current_site.domain,
                                'protocol': "https"
                }
                html_message = render_to_string('profiles/emails/reminder_12m_no_update_email_inline.html', email_context)
                plain_message = render_to_string('profiles/emails/reminder_12m_no_update_email_plain.html', email_context)
                try:
                    email = EmailMultiAlternatives(subject_prefixed, plain_message, from_email, recipients, bcc=[bcc_bac])
                    email.attach_alternative(html_message, "text/html")
                    email.send()
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            # Get the list of email adress of outdated profiles
            profileslist = ', '.join(str(p) for p in profiles)
            # Set the stdout display for the shell
            self.stdout.write(self.style.SUCCESS('Successfully sent a reminder email to profiles that did not update their profile in the past 12 months. Emails sent to: ' + profileslist))
        else:
            self.stdout.write(self.style.SUCCESS('All the profiles have at least 1 profile update in the past 12 months. No email sent.'))
