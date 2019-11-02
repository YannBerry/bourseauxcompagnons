from calendar import LocaleHTMLCalendar
from calendar import different_locale
from calendar import month_name
from calendar import monthrange
from datetime import date
from datetime import timedelta
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import gettext_lazy as _

from outings.models import Outing
from availabilities.models import Availability


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

def get_cal_locale(language):
    locales_dic={}
    locales_dic['fr']='fr_FR.utf-8'
    locales_dic['en']='en_US.utf-8'
    locales_dic['es']='es_ES.utf-8'
    locales_dic['it']='it_IT.utf-8'
    locales_dic['de']='de_DE.utf-8'
    return locales_dic.get(language)


# CALENDAR CLASSES
class Cal(LocaleHTMLCalendar):
    def __init__(self, firstweekday=0, locale=None, year=None, month=None, profile=None):
        self.year = year
        self.month = month
        self.profile = profile
        # super().__init__(firstweekday=0, locale=None)
        LocaleHTMLCalendar.__init__(self, firstweekday, locale)


class CalEvents(Cal):
    def formatday(self, day, outings, availabilities, year, month):
        if day != 0:
            this_day = date(year, month, day)
            outings_per_day = outings.filter(start_date__lte=this_day, end_date__gte=this_day)
            availabilities_per_day = availabilities.filter(start_date__lte=this_day, end_date__gte=this_day)
            o = ''
            a = ''
            for outing in outings_per_day:
                o += f"<li class='overflow-hidden'><p><a href='{ outing.get_absolute_url() }'><span class='badge badge-pill badge-info'>{ outing.title }</span></a></p</li>"
            for availability in availabilities_per_day:
                icon_checked_url = static('img/icon_available.png')
                icon_checked_alt = _('Available icon')
                icon_checked_title = _('Available')
                a += f"<a class='flex-container' href='{ availability.get_absolute_url() }'><img src='{ icon_checked_url }' class='ml-0' height='24' alt='{ icon_checked_alt }' title='{ icon_checked_title }'></a>"

        if day == 0:
            return '<td class="cal-noday">&nbsp;</td>'
        elif day !=0 and outings_per_day and availabilities_per_day:
            return f"<td class='cal-event-day'><div class='availability-flex'><span class='cal-date font-weight-bold'>{day}</span> {a}</div><ul class='cal-outing-list-bg'> {o} </ul></td>"
        elif day !=0 and outings_per_day:
            return f"<td class='cal-event-day'><span class='cal-date font-weight-bold'>{day}</span><ul class='cal-outing-list-bg'> {o} </ul></td>"
        elif day !=0 and availabilities_per_day:
            return f"<td class='cal-event-day'><div class='availability-flex'><span class='cal-date font-weight-bold'>{day}</span> {a}</div></td>"
        else:
            return f"<td><span class='cal-date'>{day}</span></td>"

    def formatweek(self, theweek, outings, availabilities, year, month):
        w = ''
        for d, weekday in theweek:
            w += self.formatday(d, outings, availabilities, year, month)
        return f'<tr> {w} </tr>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        with different_locale(self.locale):
            s = month_name[themonth]
            if withyear:
                s = '%s %s' % (s, theyear)
            return '<th colspan="5" class="month">%s</th>' % s
        # response = super().formatmonthname(theyear, themonth, withyear)
        # print(response)
        # return response

    def formatmonth(self, withyear=True):
        outings = Outing.objects.filter(author__username=self.profile)
        availabilities = Availability.objects.filter(author__username=self.profile)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="cal-table">\n'
        cal += f'<tr><th><a class="previous-month unstyled text-info">&lt;&lt;</a></th>'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'<th><a class="next-month unstyled text-info">&gt;&gt;</a></th></tr>'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, outings, availabilities, self.year, self.month)}\n'
        cal += f'</table>'
        return cal