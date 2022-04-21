from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.db.models import Q
# Translations
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language
# Sites
from django.contrib.sites.models import Site
# Sending Emails
from django.core.mail import BadHeaderError, EmailMultiAlternatives

from profiles.models import Profile


class Command(BaseCommand):
    help = 'Deactivate profiles that did not sign in to their account for more than 12 months + 2 week and inform them by email'

    def handle(self, *args, **options):
        profiles = Profile.objects.select_related('user').filter(Q(user__last_login__lt = timezone.now() - timedelta(weeks=54)) | Q(user__last_login = None))
        if profiles:
            current_site = Site.objects.get_current()
            from_email = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
            bcc_bac = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
            cur_language = get_language()
            for p in profiles:
                # Send email
                activate(p.user.language)
                subject=_("Your profile has been deactivated")
                subject_prefixed = _("[Account] {}").format(subject)
                recipients = [p.user.email]
                email_context = {'customuser': p.user,
                                'site_name': current_site.name,
                                'domain': current_site.domain,
                                'protocol': "https"
                }
                html_message = render_to_string('profiles/emails/deactivation_12m_no_signin_email_inline.html', email_context)
                plain_message = render_to_string('profiles/emails/deactivation_12m_no_signin_email_plain.html', email_context)
                try:
                    email = EmailMultiAlternatives(subject_prefixed, plain_message, from_email, recipients, bcc=[bcc_bac])
                    email.attach_alternative(html_message, "text/html")
                    email.send()
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                # Deactivate profiles
                p.public_profile = False
                p.save(update_fields=['public_profile'])
            activate(cur_language)
            # Get the list of email adress of outdated profiles
            profileslist = ', '.join(str(p) for p in profiles)
            # Set the stdout display for the shell
            self.stdout.write(self.style.SUCCESS('Successfully deactivated profiles that did not sign in in the past 12 months + 2 week and informed them by email. Emails sent to: ' + profileslist))
        else:
            self.stdout.write(self.style.SUCCESS('All the profiles have at least 1 connection in the past 12 months + 1 week. No email sent.'))
