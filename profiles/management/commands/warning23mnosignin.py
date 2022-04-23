from django.core.management.base import BaseCommand
from profiles.management.commands.utils import send_notif_email_to_profiles_inactive
# Translations
from django.utils.translation import gettext_lazy as _
from core.utils.translations import Translatable
# Sites
from django.contrib.sites.models import Site


command_name = 'warning23mnosignin'
current_site = Site.objects.get_current()

class Command(BaseCommand):
    help = 'Send a warning email to profiles that did not sign in to their account for more than 23 months'

    def handle(self, *args, **options):

        subject=Translatable(_("Warning before account deletion. Are you still using {site_name}?"), context={'site_name': current_site.name})
        html_message_name='warning_23m_no_signin_email_inline'
        plain_message_name='warning_23m_no_signin_email_plain'

        send_notif_email_to_profiles_inactive(self,
                                            nb_of_weeks_ago=100,
                                            command_name=command_name,
                                            subject=subject,
                                            html_message_name=html_message_name,
                                            plain_message_name=plain_message_name,
        )
