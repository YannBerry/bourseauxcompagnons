from django.core.management.base import BaseCommand
from profiles.management.commands.utils import send_notif_email_to_profiles_inactive
# Translations
from django.utils.translation import gettext_lazy as _


command_name = 'deactivation12mnosignin'

class Command(BaseCommand):
    help = 'Deactivate profiles that did not sign in to their account for more than 12 months + 2 week and inform them by email'

    def handle(self, *args, **options):

        subject=_("Your profile has been deactivated")
        html_message_name='deactivation_12m_no_signin_email_inline'
        plain_message_name='deactivation_12m_no_signin_email_plain'

        send_notif_email_to_profiles_inactive(self,
                                            nb_of_weeks_ago=54,
                                            command_name=command_name,
                                            subject=subject,
                                            html_message_name=html_message_name,
                                            plain_message_name=plain_message_name,
                                            profile_deactivation=True,
        )
