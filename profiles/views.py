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
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry
# Sending Emails
from django.core.mail import EmailMessage, BadHeaderError, EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# Exporting Excel files
from datetime import datetime
from datetime import date
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import NamedStyle, Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
#import string
from openpyxl.drawing.image import Image
from openpyxl.chart import PieChart, Reference
from openpyxl.worksheet.pagebreak import RowBreak, Break, ColBreak
import os
# Calendar
from core.utils import CalOutings
from django.utils.safestring import mark_safe
from calendar import monthrange

from profiles.models import Profile, CustomUser
from activities.models import Activity
from profiles.forms import ProfileCreationForm, AccountForm, ProfileForm, ContactProfileForm

from django.contrib.gis.geos import Point
longitude = 8.191788
latitude = 48.761681
user_location = Point(longitude, latitude, srid=4326)


# FUNCTIONS USED FOR THE CALENDAR
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return date.today()
    
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


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
        context['around_me'] = self.request.GET.get('around_me')
        # availability_area_geo_str_json = self.request.GET.get('availability_area_geo')
        # if availability_area_geo_str_json:
        #     availability_area_geo_json = fromstr(availability_area_geo_str_json) # default SRID for json: 4326
        #     context['availability_area_geo'] = availability_area_geo_json or None
                # use today's date for the calendar
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_loc = self.request.user.profile.location
            main_q = Profile.objects.exclude(user=self.request.user).filter(public_profile='True').annotate(distance=Distance('location', user_loc)).order_by('distance')
        else:
            main_q = Profile.objects.filter(public_profile='True')
        selected_activities = self.request.GET.getlist('a')
        activities_in_current_language = 'activities__name_{}'.format(get_language())
        around_me = self.request.GET.get('around_me')
        availability_area_geo = self.request.GET.get('availability_area_geo')
        # Defining querysets of each criteria
        if selected_activities and self.request.user.is_authenticated:
            selected_activities_q = main_q.filter(
                eval(' | '.join(f'Q({ activities_in_current_language }="{ selected_activity }")' for selected_activity in selected_activities)),
                public_profile='True'
            ).distinct('distance', 'last_update', 'user_id')
        elif selected_activities:
            selected_activities_q = main_q.filter(
                eval(' | '.join(f'Q({ activities_in_current_language }="{ selected_activity }")' for selected_activity in selected_activities)),
                public_profile='True'
            ).distinct('last_update', 'user_id')
        if availability_area_geo:
            availability_area_geo_q = main_q.filter(availability_area_geo__intersects=availability_area_geo)
        if around_me:
            around_me_q = main_q.filter(location__distance_lte=(user_loc, 50000))
        # Defining the queryset according to the criteria selected by the internaut
        if selected_activities and availability_area_geo and around_me:
            queryset = selected_activities_q.intersection(availability_area_geo_q, around_me_q)
        elif selected_activities and availability_area_geo:
            queryset = selected_activities_q.intersection(availability_area_geo_q)
        elif selected_activities and around_me:
            queryset = selected_activities_q.intersection(around_me_q)
        elif availability_area_geo and around_me:
            queryset = availability_area_geo_q.intersection(around_me_q)
        elif selected_activities:
            queryset = selected_activities_q
            self.nb_of_results = len(queryset)
        elif availability_area_geo:
            queryset = availability_area_geo_q
            self.nb_of_results = len(queryset)
        elif around_me:
            queryset = around_me_q
            self.nb_of_results = len(queryset)
        else:
            queryset = main_q
        return queryset


class ProfileDetailView(DetailView):
    '''A view for the web surfer to detail a specific profile'''

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        profile = get_object_or_404(Profile, pk=CustomUser.objects.get(username=self.kwargs['username']).pk)
        if profile.availability_area_geo is not None:
            poly_tuple = profile.availability_area_geo.coords[0]
            context['availability_area_geo_poly'] = [[i[0], i[1]] for i in poly_tuple] or None
        # Calendar Context
        d = get_date(self.request.GET.get('month', None))
        locales_dic={}
        locales_dic['fr']='fr_FR.utf-8'
        locales_dic['en']='en_US.utf-8'
        locales_dic['es']='es_ES.utf-8'
        locales_dic['it']='it_IT.utf-8'
        locales_dic['de']='de_DE.utf-8'
        cal = CalOutings(year=d.year, month=d.month, profile=self.kwargs['username'], locale=locales_dic.get(get_language()))
        html_cal = cal.formatmonth(withyear=True)
        context['cal_outings'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
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
        html_message = render_to_string('profiles/profile_register_email_inline.html', {'customuser': self.object})
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

# VIEWS FOR EXPORTING

def export_profiles_to_xlsx(request):
    '''A view to export all the profiles to an xlsx format'''
    profiles_queryset = Profile.objects.all()
    activities = Activity.objects.all()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={date}_bac_profiles.xlsx'.format(date=datetime.now().strftime('%Y%m%d'))
    workbook = Workbook()
    
    ### STYLES ###
    # Colors
    dark_red = 'FFC00000'
    # Bold
    bold_st = NamedStyle(name="bold_st")
    bold_st.font = Font(name='Calibri', bold=True, color='FF000000')
    # Main title row
    main_title = NamedStyle(name="main_title")
    main_title.font = Font(name='Calibri', bold=True, color='FF000000', size='20')
    main_title.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    main_title.border = Border(
        left=Side(border_style='thin', color='FF00008F'),
        right=Side(border_style='thin', color='FF00008F'),
        top=Side(border_style='thin', color='FF00008F'),
        bottom=Side(border_style='thin', color='FF00008F')
    )
    main_title.fill = PatternFill(fill_type='solid', fgColor='FF4080C6')
    # First row
    first_row = NamedStyle(name="first_row")
    first_row.font = Font(name='Calibri', bold=True, color='FFFFFFFF')
    first_row.alignment = Alignment(wrap_text=True, vertical='center')
    first_row.border = Border(
        left=Side(border_style='thin', color='FF000000'),
        right=Side(border_style='thin', color='FF000000'),
        top=Side(border_style='thin', color='FF000000'),
        bottom=Side(border_style='thin', color='FF000000')
    )
    first_row.fill = PatternFill(fill_type='solid', fgColor='FF6F6F6F')
    # Values row
    values_st = NamedStyle(name="values")
    values_st.font = Font(name='Calibri', color='FF000000')
    values_st.alignement = Alignment(wrap_text=True, vertical='top')
    values_st.border = Border(
        left=Side(border_style='thin', color='FF000000'),
        right=Side(border_style='thin', color='FF000000')
    )
    # Date format
    date_format = NamedStyle(name="date_format")
    date_format.font = Font(name='Calibri', color='FF000000')
    date_format.alignement = Alignment(wrap_text=True, vertical='top')
    date_format.border = Border(
        left=Side(border_style='thin', color='FF000000'),
        right=Side(border_style='thin', color='FF000000')
    )
    date_format.number_format='YYYY-MM-DD'
    
    ### PROFILE WORKSHEET ###
    # Creating the worksheet
    profiles_worksheet = workbook.active
    # Page setup (print settings)
    profiles_worksheet.page_setup.orientation = 'landscape' #profiles_worksheet.ORIENTATION_PORTRAIT
    profiles_worksheet.page_setup.paperSize = profiles_worksheet.PAPERSIZE_A4
    profiles_worksheet.page_setup.fitToPage = True
    profiles_worksheet.page_setup.fitToHeight = False
    profiles_worksheet.page_margins.top = 0.75 # inches (1,91 cm)
    profiles_worksheet.page_margins.bottom = 0.75 # inches (1,91 cm)
    profiles_worksheet.page_margins.left = 0.7 # inches (1,78 cm)
    profiles_worksheet.page_margins.right = 0.7 # inches (1,78 cm)
    profiles_worksheet.page_margins.header = 0.3 # inches (0,76 cm)
    profiles_worksheet.page_margins.footer = 0.3 # inches (0,76 cm)
    profiles_worksheet.print_options.horizontalCentered = True
    profiles_worksheet.sheet_view.view = 'pageLayout'
    #profiles_worksheet.print_area = profiles_worksheet.dimensions
    # Title
    profiles_worksheet.title = 'Profiles'
    # First row of the table
    attributes = [
        'username',
        'first name',
        'last name',
        'public profile',
        'introduction',
        'list of courses',
        'activities',
        'birthdate',
    ]

    # HEADER & FOOTER
    profiles_worksheet.oddFooter.center.text = "bourseauxcompagnons.fr"
    profiles_worksheet.oddFooter.center.size = 11
    
    # Initializing variables
    row_breaks_list = []
    row = 1

    # COVER PAGE
        # Blank row
    profiles_worksheet.row_dimensions[row].height = 80
        # Logo
    row += 1
    dirname = os.path.dirname(os.path.dirname(__file__))
    filename = os.path.join(dirname, 'collected_static/img/icon_group_map.png')
    img = Image(filename)
    anchor = 'D2'
        # Confidential
    CP_confidential = profiles_worksheet.cell(column=len(attributes)-1, row=row)
    CP_confidential.value = "CONFIDENTIEL"
    CP_confidential.font = Font(name='Calibri', bold=True, color=dark_red)
        # Title
    row += 1
    profiles_worksheet.add_image(img, anchor)
    CP_title = profiles_worksheet.cell(column=4, row=row)
    CP_title.value = "LISTE COMPLETE DES PROFILS\n(sans les coordonnées personnelles)"
    profiles_worksheet.merge_cells(start_row=row, start_column=4, end_row=row, end_column=len(attributes)-2)
    profiles_worksheet.row_dimensions[row].height = 600
    CP_title.font = Font(name='Calibri', bold=True, color='FF000000', size='20')
    CP_title.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        # Date
    row += 1
    CP_date = profiles_worksheet.cell(column=len(attributes)-1, row=row)
    CP_date.value = "Le {}".format(date.today())
        # Blank row
    row += 1
        # Page break
    row_breaks_list.append(Break(id=row))
    
    # OVERVIEW
        # Title
    row += 1
    O_title = profiles_worksheet.cell(column=1, row=row)
    O_title.value = "SYNTHESE"
    O_title.style = main_title
    profiles_worksheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(attributes))
    profiles_worksheet.row_dimensions[row].height = 40
        # Blank row
    row += 1
        # Content
    row += 1
    O_publication_date = profiles_worksheet.cell(column=1, row=row)
    O_publication_date.value = "Date d'export"
    O_publication_date.style = bold_st
    profiles_worksheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
    O_publication_date_value = profiles_worksheet.cell(column=3, row=row)
    O_publication_date_value.value = date.today()
    row += 1
    O_nb_of_profiles = profiles_worksheet.cell(column=1, row=row)
    O_nb_of_profiles.value = "Nombre de profils"
    O_nb_of_profiles.style = bold_st
    profiles_worksheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
    O_nb_of_profiles_value = profiles_worksheet.cell(column=3, row=row)
    O_nb_of_profiles_value.value = len(profiles_queryset)
        # Blank row
    row += 1
        # Page break
    row_breaks_list.append(Break(id=row))
    
    # TABLE
    row += 1
    first_row_of_table = row
        # Creating the first row
    for col_num, col_title in enumerate(attributes,1):
        cell = profiles_worksheet.cell(row=first_row_of_table, column=col_num, value=col_title.upper())
        cell.style = first_row
        column_dimensions = profiles_worksheet.column_dimensions[get_column_letter(col_num)]
        if col_title == 'introduction':
            column_dimensions.width = 45
        elif col_title == 'list of courses':
            column_dimensions.width = 45
        elif col_title == 'activities':
            column_dimensions.width = 35
        else:
            max_length = 0
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
            adjusted_width = (max_length + 2)*1.2
            column_dimensions.width = adjusted_width
    
        # Freezing the first row
    # freezing_cell = "A{}".format(first_row_of_table+1)
    # profiles_worksheet.freeze_panes = profiles_worksheet[freezing_cell]
    
        # Adding the values
    values_row = first_row_of_table
    for profile in profiles_queryset:
        values_row += 1
        values = [
            (profile.user.username, values_st),
            (profile.user.first_name, values_st),
            (profile.user.last_name, values_st),
            (profile.public_profile, values_st),
            (profile.introduction, values_st),
            (profile.list_of_courses, values_st),
            (', '.join([str(i) for i in profile.activities.all()]), values_st),
            (profile.birthdate, date_format),
        ]
        for col_num, (col_value, col_format) in enumerate(values, 1):
            cell = profiles_worksheet.cell(row=values_row, column=col_num, value=col_value)
            cell.style = col_format
    
        # Adding filtering
    profiles_worksheet_dim = profiles_worksheet.dimensions
    profiles_worksheet_dim_list = list(profiles_worksheet_dim)
    profiles_worksheet_dim_list[1] = str(first_row_of_table)
    profiles_worksheet_dim = "".join(profiles_worksheet_dim_list)
    #number_to_letter = []
    # for index, letter in enumerate(string.ascii_uppercase, 1):
    #     number_to_letter.append((index, letter))
    # print(number_to_letter)
    # print(get_column_letter(1))
    profiles_worksheet.auto_filter.ref = profiles_worksheet_dim

    # Adding the declared page breaks to the worksheet
    profiles_worksheet.page_breaks = (RowBreak(brk=row_breaks_list), ColBreak())

    ### STAT WORKSHEET ###
    # Creating the worksheet
    stat_worksheet = workbook.create_sheet("Stat")
    
    # Distribution of profiles by activity
    activities_distribution = [('Activity', 'Number of profiles')]
    activities_in_current_language = 'activities__name_{}'.format(get_language())
    
    for activity in activities:
        activity_filter = {}
        activity_filter[activities_in_current_language] = activity
        number_of_profiles = Profile.objects.filter(**activity_filter).count()
        activities_distribution.append((str(activity), number_of_profiles))
    for row in activities_distribution:
        stat_worksheet.append(row)
    
    piechart_profiles_by_activity = PieChart()
    labels = Reference(stat_worksheet, min_col = 1, min_row = 2, max_row = activities.count() + 1)
    data = Reference(stat_worksheet, min_col = 2, min_row = 1, max_row = activities.count() + 1)
    piechart_profiles_by_activity.add_data(data, titles_from_data=True)
    piechart_profiles_by_activity.set_categories(labels)
    piechart_profiles_by_activity.title = "Profiles distribution by activities"

    stat_worksheet.add_chart(piechart_profiles_by_activity, "D1")
    
    ### SAVING WORKBOOK ###
    workbook.save(response)

    return response