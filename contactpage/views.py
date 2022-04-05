from django.shortcuts import render, redirect
from django.http import HttpResponse
# Messages
from django.contrib import messages
# Translation
from django.utils.translation import gettext_lazy as _
# Sending Emails
from django.core.mail import EmailMessage, BadHeaderError

from contactpage.forms import ContactForm


def ContactPageView(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    ['contact@bourseauxcompagnons.fr']
                )
                email.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            msg = _('Your message as been sent successfully. We will get back to you as soon as possible!')
            messages.add_message(request, messages.SUCCESS, msg)
            return redirect('contactpage:contact-page')
    else:
        if request.user.is_authenticated:
            form = ContactForm(initial={'from_email': request.user.email})
        else:
            form = ContactForm()
    return render(request, "contactpage/contactpage.html", {'form': form})
