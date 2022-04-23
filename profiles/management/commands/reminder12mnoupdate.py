from django.core.management.base import BaseCommand
from profiles.management.commands.utils import send_notif_email_to_profiles_outdated
# Translations
from django.utils.translation import gettext_lazy as _


command_name = 'reminder12mnoupdate'

class Command(BaseCommand):
    help = 'Send a reminder email to profiles that did not update their account in the past 12 months'

    def handle(self, *args, **options):

        subject=_("Think to update your profile!")
        html_message_name='reminder_12m_no_update_email_inline'
        plain_message_name='reminder_12m_no_update_email_plain'
        
        send_notif_email_to_profiles_outdated(self,
                                            nb_of_weeks_ago=52,
                                            command_name=command_name,
                                            subject=subject,
                                            html_message_name=html_message_name,
                                            plain_message_name=plain_message_name,
        )