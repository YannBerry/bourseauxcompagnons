from django.core.mail import EmailMessage, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect

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
            return redirect('contactpage:email-sent')
    else:
        if request.user.is_authenticated:
            form = ContactForm(initial={'from_email': request.user.email})
        else:
            form = ContactForm()
    return render(request, "contactpage/contactpage.html", {'form': form})
