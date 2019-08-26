from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
# Translation
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
# GeoDjango
from django.contrib.gis.db.models.functions import Distance
# Sending Emails
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from profiles.models import Profile, CustomUser
from activities.models import Activity
from profiles.forms import ProfileCreationForm, AccountForm, ProfileForm, ContactProfileForm

from django.contrib.gis.geos import Point
longitude = 8.191788
latitude = 48.761681
user_location = Point(longitude, latitude, srid=4326)

# VIEWS FOR ANONYM WEB SURFERS

class ProfileListView(ListView):
    '''
    Display the all the public profiles by default.
    If a filter is activated it displays the profiles according to the filter.
    '''
    template_name = "profiles/profile_list.html"
    nb_of_results = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['nb_of_results'] = self.nb_of_results
        context['selected_activities'] = self.request.GET.getlist('a') or None
        return context

    def get_queryset(self):
        if self.request.GET.getlist('a'):
            activities_in_current_language = 'activities__name_{}'.format(get_language())
            selected_activities = self.request.GET.getlist('a')
            queryset = Profile.objects.filter(
                eval(' | '.join(f'Q({ activities_in_current_language }="{ selected_activity }")' for selected_activity in selected_activities)),
                public_profile='True'
            ).distinct('last_update', 'user_id')
            self.nb_of_results = len(queryset)
        else:
            queryset = Profile.objects.annotate(distance=Distance('location', user_location)).order_by('distance').filter(public_profile='True')
            #queryset = Profile.objects.filter(public_profile='True')
        return queryset


class ProfileDetailView(DetailView):
    '''A view for the web surfer to detail a specific profile'''
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        profile = get_object_or_404(Profile, pk=CustomUser.objects.get(username=self.kwargs['username']).pk)
        if profile.availability_area_geo is not None:
            poly_tuple = profile.availability_area_geo.coords[0]
            context['availability_area_geo_poly'] = [[i[0], i[1]] for i in poly_tuple] or None
        return context

    def get_object(self):
        return get_object_or_404(Profile, pk=CustomUser.objects.get(username=self.kwargs['username']).pk)

def ContactProfileView(request, **kwargs):
    '''A view for the web surfer to send an email to the profile through a contact form.'''
    if request.method == 'POST':
        form = ContactProfileForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            subject_prefixed = '[bourseauxcompagnons] ' + subject 
            from_email = form.cleaned_data['from_email']
            recipients = [CustomUser.objects.get(username=kwargs['username']).email]
            contact_message = form.cleaned_data['message']
            html_message = render_to_string(
                'profiles/contact_profile_email_inline.html',
                {'profile_contacted': CustomUser.objects.get(username=kwargs['username']).username,
                'language_code' : get_language(),
                'profile_making_contact': request.user.username,
                'message': contact_message
                }
            )
            plain_message = strip_tags(html_message)
            try:
                email = EmailMultiAlternatives(
                    subject_prefixed,
                    plain_message,
                    from_email,
                    recipients,
                    bcc=['contact@bourseauxcompagnons.fr'],
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('profiles:contact-profile-done', username=kwargs['username'])
    else:
        if request.user.is_authenticated:
            form = ContactProfileForm(initial={'from_email': request.user.email,
                                                'subject': _('Initial contact'),
                                                'message': _('Hi ')+kwargs['username']+',\n'})
        else:
            form = ContactProfileForm()
    return render(request, "profiles/contact_profile_form.html", {'form': form, 'username': kwargs['username']})


class ProfileRegisterView(SuccessMessageMixin, CreateView):
    '''A view for the web surfer to create a profile'''
    form_class = ProfileCreationForm
    template_name = 'profiles/profile_register.html'
    success_url = reverse_lazy('my-profile')
    success_message = _("WARNING : your profile is public by default. That is to say that it will be displayed "
                        "in the profile list available on bourseauxcompagnons. Click on "
                        "'Update my profile' to complete it or make it private."
                        )

    def form_valid(self, form):
        '''
        1. Save the valid form (useless because already saved through ProfileCreationForm but it provides me with self.object which is the customuser)
        2. Send an confirmation email to the new profile
        3. Login the new profile
        4. Redirect to success_url.

        No authentication.
        '''
        response = super().form_valid(form)

        subject="Profil créé"
        subject_prefixed = '[Compte] ' + subject 
        recipients = [self.object.email]
        html_message = render_to_string('profiles/profile_register_email.html', {'customuser': self.object})
        plain_message = strip_tags(html_message)
        send_mail(subject_prefixed, plain_message, "Bourse aux compagnons <contact@bourseauxcompagnons.fr>", recipients, html_message=html_message)
        
        login(self.request, self.object)
        
        return response


# VIEWS FOR AUTHENTICATED PROFILES

class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    '''A view for the authenticated profile to update its profile.'''
    form_class = ProfileForm

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_object(self):
        return get_object_or_404(Profile, pk=CustomUser.objects.get(username=self.kwargs['username']).pk)
    '''
    def form_valid(self, form):
        coordinates = form.cleaned_data['location'].split(',')
        print(coordinates)
        form.instance.location = Point(float(coordinates[0]),float(coordinates[1]))
        return super().form_valid(form)
    '''



class AccountUpdateView(UserPassesTestMixin, UpdateView):
    '''A view for the authenticated profile to update its profile account settings.'''
    form_class = AccountForm
    template_name = 'registration/account_form.html'
    success_url = reverse_lazy('my-profile')

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])


class AccountDeleteView(UserPassesTestMixin, DeleteView):
    '''A view for the authenticated profile to delete its own profile and account'''
    model = CustomUser
    template_name = 'registration/account_confirm_delete.html'
    success_url = reverse_lazy('homepage')

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])