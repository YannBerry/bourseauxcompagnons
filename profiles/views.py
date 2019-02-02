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
# Sending Emails
from django.core.mail import EmailMessage, BadHeaderError
from django.core.mail import send_mail
from django.template.loader import render_to_string

from profiles.models import Profile, CustomUser
from activities.models import Activity
from profiles.forms import ProfileCreationForm, AccountForm, ProfileForm, ContactProfileForm


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
            selected_activities = self.request.GET.getlist('a')
            queryset = Profile.objects.filter(
                eval(' | '.join(f'Q(activities__name="{ selected_activity }")' for selected_activity in selected_activities)),
                public_profile='True'
            ).distinct('last_update', 'user_id')
            self.nb_of_results = len(queryset)
        else:
            queryset = Profile.objects.filter(public_profile='True')
        return queryset


class ProfileDetailView(DetailView):
    '''A view for the web surfer to detail a specific profile'''
    def get_object(self):
        return get_object_or_404(Profile, pk=CustomUser.objects.get(username=self.kwargs['username']).pk)

def ContactProfileView(request, **kwargs):
    '''A view for the web surfer to send an email to the profile through a contact form.'''
    if request.method == 'POST':
        form = ContactProfileForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            recipient = [CustomUser.objects.get(username=kwargs['username']).email]
            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    recipient,
                )
                email.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('profiles:contact-profile-done', username=kwargs['username'])
    else:
        if request.user.is_authenticated:
            form = ContactProfileForm(initial={'from_email': request.user.email, 'subject': '[bourseauxcompagnons] Prise de contact', 'message': 'Bonjour '+kwargs['username']+',\n'})
        else:
            form = ContactProfileForm()
    return render(request, "profiles/contact_profile_form.html", {'form': form, 'username': kwargs['username']})


class ProfileRegisterView(SuccessMessageMixin, CreateView):
    '''A view for the web surfer to create a profile'''
    form_class = ProfileCreationForm
    template_name = 'profiles/profile_register.html'
    success_url = reverse_lazy('my-profile')
    success_message = "IMPORTANT : par défault votre profil est public. C'est à dire qu'il apparait dans la liste des profils consultables sur bourseauxcompagnons. Cliquez sur 'Mettre à jour mon profil' pour le compléter ou le privatiser."

    def form_valid(self, form):
        '''
        1. Save the valid form (useless because already saved through ProfileCreationForm but it provides me with self.object which is the customuser)
        2. Login the new profile
        3. Redirect to success_url.

        No authentication.
        '''
        response = super().form_valid(form)
        recipient = self.object.email
        message = render_to_string('profiles/profile_register_email.html', {'customuser': self.object})
        send_mail("Création de votre compte", message, "Bourse aux compagnons <contact@bourseauxcompagnons.fr>", [recipient])
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