from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from profiles.management.commands.utils import send_notif_email, remove_account_inactivity_email_sent
# Translations
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language
# Sites
from django.contrib.sites.models import Site

from profiles.models import Profile


command_name = 'reminder6mnosignin'

class Command(BaseCommand):
    help = 'Send a reminder email to profiles that did not sign in to their account for more than 6 months'

    def handle(self, *args, **options):
        ### Get the queryset ###
        referencedate = timezone.now() - timedelta(weeks=26)
        profiles_inactive = Profile.objects.select_related('user').filter(Q(user__last_login__lt = referencedate) | Q(user__last_login = None)).exclude(user__inactivity_email_sent__contains=command_name)
        profiles_active_again = Profile.objects.filter(Q(user__inactivity_email_sent__contains=command_name) & Q(user__last_login__gte = referencedate))

        ### Treat the case of profiles_active_again ###
        if profiles_active_again:
            for p in profiles_active_again:
                remove_account_inactivity_email_sent(command_name=command_name, profile=p)

        ### Treat the case of profiles_inactive ###
        if profiles_inactive:
            current_site = Site.objects.get_current()
            cur_language = get_language()
            for p in profiles_inactive:
                # Send reminder email
                activate(p.user.language)
                subject=_("Are you still using {}?").format(current_site.name)
                send_notif_email(profile=p,
                                site_name=current_site.name,
                                site_domain = current_site.domain,
                                subject=subject,
                                html_message_name='reminder_6m_no_signin_email_inline',
                                plain_message_name='reminder_6m_no_signin_email_plain',
                                command_name=command_name
                )
            activate(cur_language)


        ### Set the stdout display for the shell ###
        # Get the list of email adress of profiles_inactive
        profiles_inactive_list = ', '.join(str(p) for p in profiles_inactive)
        # Get the list of email adress of profiles_active_again
        profiles_active_again_list = ', '.join(str(p) for p in profiles_active_again)
        # Defining stdout messages
        main_message_profiles_inactive = 'Successfully sent a reminder email to profiles that did not sign in in the past 6 months. Emails sent to: ' + profiles_inactive_list
        main_message_no_profiles_inactive = 'All the profiles have at least 1 connection in the past 6 months or are already informed by mail. No email sent.'
        extra_message_profiles_active_again = '\nList of profiles back to activity: ' + profiles_active_again_list
        # Set the stdout display for the shell
        if profiles_inactive:
            if profiles_active_again_list:
                self.stdout.write(self.style.SUCCESS(main_message_profiles_inactive + extra_message_profiles_active_again))
            else:
                self.stdout.write(self.style.SUCCESS(main_message_profiles_inactive))
        else:
            if profiles_active_again_list:
                self.stdout.write(self.style.SUCCESS(main_message_no_profiles_inactive + extra_message_profiles_active_again))
            else:
                self.stdout.write(self.style.SUCCESS(main_message_no_profiles_inactive))
