from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.core.mail import BadHeaderError
from django.http import HttpResponse
from django.db.models import Q
# Translations
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate, get_language
# Sites
from django.contrib.sites.models import Site
# Sending Emails
from django.core.mail import BadHeaderError, EmailMultiAlternatives

from profiles.models import CustomUser, Profile


def get_profiles_inactive(referencedate, command_name):
    return Profile.objects.select_related('user').filter(Q(user__last_login__lt = referencedate) | Q(user__last_login = None)).exclude(user__inactivity_email_sent__contains=command_name)

def get_profiles_active_again(referencedate, command_name):
    return Profile.objects.filter(Q(user__inactivity_email_sent__contains=command_name) & Q(user__last_login__gte = referencedate))

def get_profiles_outdated(referencedate, command_name):
    return Profile.objects.select_related('user').filter(last_update__lt = referencedate).exclude(user__inactivity_email_sent__contains=command_name)

def get_profiles_updated_again(referencedate, command_name):
    return Profile.objects.filter(Q(user__inactivity_email_sent__contains=command_name) & Q(last_update__gte = referencedate))

def add_account_inactivity_email_sent(command_name, profile):
    """
    Function to register that a profile was detected as inactive for X month or did't update for X months
    """
    p_account = CustomUser.objects.get(email=profile.user.email)
    p_account.inactivity_email_sent.append(command_name)
    p_account.save(update_fields=['inactivity_email_sent'])

def remove_account_inactivity_email_sent(command_name, profile):
    """
    Function to register that a profile sign in or updated again its account
    """
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

def send_notif_email_to_profiles_inactive(self, nb_of_weeks_ago, command_name, subject, html_message_name, plain_message_name, profile_deactivation=False, profile_deletion=False):

    ### Get the queryset ###
    referencedate = timezone.now() - timedelta(weeks=nb_of_weeks_ago)
    profiles_inactive = get_profiles_inactive(referencedate=referencedate, command_name=command_name)
    profiles_active_again = get_profiles_active_again(referencedate=referencedate, command_name=command_name)
    
    ### Treat the case of profiles_active_again ###
    if profiles_active_again:
        for p in profiles_active_again:
            remove_account_inactivity_email_sent(command_name=command_name, profile=p)
    
    ### Treat the case of profiles_inactive ###
    if profiles_inactive:
        current_site = Site.objects.get_current()
        cur_language = get_language()
        for p in profiles_inactive:
            # Send email in profile prefered language (the one set in its account which is 'fr' by default)
            activate(p.user.language)
            send_notif_email(profile=p,
                            site_name=current_site.name,
                            site_domain = current_site.domain,
                            subject=subject,
                            html_message_name=html_message_name,
                            plain_message_name=plain_message_name,
                            command_name=command_name
            )
            # Deactivate profile if asked
            if profile_deactivation:
                p.public_profile = False
                p.save(update_fields=['public_profile'])
            # Delete profile if asked
            if profile_deletion:
                p_account = CustomUser.objects.get(email=p.user.email)
                p_account.delete()
        activate(cur_language)

    ### Set the stdout display for the shell ###
    profiles_inactive_list = ', '.join(str(p) for p in profiles_inactive)
    profiles_active_again_list = ', '.join(str(p) for p in profiles_active_again)
    # Defining stdout messages
    main_message_profiles_inactive = 'Successfully sent an email to profiles that did not sign in in the past {} weeks. Emails sent to: {}'.format(nb_of_weeks_ago, profiles_inactive_list)
    main_message_no_profiles_inactive = 'All the profiles have at least 1 connection in the past {} weeks or are already informed by mail. No email sent.'.format(nb_of_weeks_ago)
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

def send_notif_email_to_profiles_outdated(self, nb_of_weeks_ago, command_name, subject, html_message_name, plain_message_name):

    ### Get the queryset ###
    referencedate = timezone.now() - timedelta(weeks=nb_of_weeks_ago)
    profiles_outdated = get_profiles_outdated(referencedate=referencedate, command_name=command_name)
    profiles_updated_again = get_profiles_updated_again(referencedate=referencedate, command_name=command_name)
    
    ### Treat the case of profiles_updated_again ###
    if profiles_updated_again:
        for p in profiles_updated_again:
            remove_account_inactivity_email_sent(command_name=command_name, profile=p)
    
    ### Treat the case of profiles_outdated ###
    if profiles_outdated:
        current_site = Site.objects.get_current()
        cur_language = get_language()
        for p in profiles_outdated:
            # Send email
            activate(p.user.language)
            send_notif_email(profile=p,
                            site_name=current_site.name,
                            site_domain = current_site.domain,
                            subject=subject,
                            html_message_name=html_message_name,
                            plain_message_name=plain_message_name,
                            command_name=command_name
            )                
        activate(cur_language)
    
    ### Set the stdout display for the shell ###
    profiles_outdated_list = ', '.join(str(p) for p in profiles_outdated)
    profiles_updated_again_list = ', '.join(str(p) for p in profiles_updated_again)
    # Defining stdout messages
    main_message_profiles_outdated = 'Successfully sent an email to profiles that did not update their profile in the past {} weeks. Emails sent to: {}'.format(nb_of_weeks_ago, profiles_outdated_list)
    main_message_no_profiles_outdated = 'All the profiles have at least 1 profile update in the past {} weeks or are already informed by mail. No email sent.'.format(nb_of_weeks_ago)
    extra_message_profiles_updated_again = '\nList of profiles back to update: ' + profiles_updated_again_list
    # Set the stdout display for the shell
    if profiles_outdated:
        if profiles_updated_again_list:
            self.stdout.write(self.style.SUCCESS(main_message_profiles_outdated + extra_message_profiles_updated_again))
        else:
            self.stdout.write(self.style.SUCCESS(main_message_profiles_outdated))
    else:
        if profiles_updated_again_list:
            self.stdout.write(self.style.SUCCESS(main_message_no_profiles_outdated + extra_message_profiles_updated_again))
        else:
            self.stdout.write(self.style.SUCCESS(main_message_no_profiles_outdated))