from django.template.loader import render_to_string
from django.core.mail import BadHeaderError
from django.http import HttpResponse
# Translations
from django.utils.translation import gettext_lazy as _
# Sending Emails
from django.core.mail import BadHeaderError, EmailMultiAlternatives

from profiles.models import CustomUser


def add_account_inactivity_email_sent(command_name, profile):
    # Function to register that a profile was detected as inactive for X month or did't
    # update for X months
    p_account = CustomUser.objects.get(email=profile.user.email)
    p_account.inactivity_email_sent.append(command_name)
    p_account.save(update_fields=['inactivity_email_sent'])


def remove_account_inactivity_email_sent(command_name, profile):
    # Function to register that a profile sign in or updated again its account
    p_account = CustomUser.objects.get(email=profile.user.email)
    p_account.inactivity_email_sent.remove(command_name)
    p_account.save(update_fields=['inactivity_email_sent'])

def send_notif_email(profile, site_name, site_domain, subject, html_message_name, plain_message_name, command_name):
    from_email = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
    bcc_bac = "Bourse aux compagnons <contact@bourseauxcompagnons.fr>"
    subject_prefixed = _("[Account] {}").format(subject)
    recipients = [profile.user.email]
    email_context = {'customuser': profile.user,
                    'site_name': site_name,
                    'domain': site_domain,
                    'protocol': "https"
    }
    html_message = render_to_string('profiles/emails/{}.html'.format(html_message_name), email_context)
    plain_message = render_to_string('profiles/emails/{}.html'.format(plain_message_name), email_context)
    try:
        email = EmailMultiAlternatives(subject_prefixed, plain_message, from_email, recipients, bcc=[bcc_bac])
        email.attach_alternative(html_message, "text/html")
        email.send()
        add_account_inactivity_email_sent(command_name=command_name, profile=profile)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')