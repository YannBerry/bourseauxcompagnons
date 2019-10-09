from calendar import LocaleHTMLCalendar
from calendar import different_locale
from calendar import month_name

from outings.models import Outing


class Cal(LocaleHTMLCalendar):
    def __init__(self, firstweekday=0, locale=None, year=None, month=None, profile=None):
        self.year = year
        self.month = month
        self.profile = profile
        # super().__init__(firstweekday=0, locale=None)
        LocaleHTMLCalendar.__init__(self, firstweekday, locale)


class CalOutings(Cal):
    def formatday(self, day, outings):
        outings_per_day = outings.filter(start_date__day=day)
        d = ''
        for outing in outings_per_day:
            d += f'<li class="overflow-hidden"><p><a href="{ outing.get_absolute_url() }"><span class="badge badge-pill badge-info">{ outing.title }</span></a></p</li>'

        if day == 0:
            return '<td class="cal_noday">&nbsp;</td>'
        elif day !=0 and outings_per_day:
            return f"<td class='cal-outing-day-bg'><span class='cal-date font-weight-bold'>{day}</span><ul class='cal-outing-list-bg'> {d} </ul></td>"
        else:
            return f"<td><span class='cal-date'>{day}</span></td>"

    def formatweek(self, theweek, outings):
        w = ''
        for d, weekday in theweek:
            w += self.formatday(d, outings)
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
        outings = Outing.objects.filter(author__username=self.profile, start_date__year=self.year, start_date__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="cal-table">\n'
        cal += f'<tr><th><a class="previous-month unstyled text-info">&lt;&lt;</a></th>'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'<th><a class="next-month unstyled text-info">&gt;&gt;</a></th></tr>'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, outings)}\n'
        cal += f'</table>'
        print(cal)
        return cal