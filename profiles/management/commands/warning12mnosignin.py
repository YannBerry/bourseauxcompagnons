from django.core.management.base import BaseCommand
from profiles.management.commands.utils import send_notif_email_to_profiles_inactive
# Translations
from django.utils.translation import gettext_lazy as _


command_name = 'warning12mnosignin'

class Command(BaseCommand):
    help = 'Send a warning email to profiles that did not sign in to their account for more than 12 months'

    def handle(self, *args, **options):

        subject=_("Warning before profile deactivation")
        html_message_name='warning_12m_no_signin_email_inline'
        plain_message_name='warning_12m_no_signin_email_plain'

        send_notif_email_to_profiles_inactive(self,
                                            nb_of_weeks_ago=52,
                                            command_name=command_name,
                                            subject=subject,
                                            html_message_name=html_message_name,
                                            plain_message_name=plain_message_name,
        )
