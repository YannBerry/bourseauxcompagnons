from django.contrib import admin

from availabilities.models import Availability


class AvailabilityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('start_date',)}
    list_display = ['start_date', 'end_date', 'author']
    autocomplete_fields = ['author']

    class Meta:
        model = Availability


admin.site.register(Availability, AvailabilityAdmin)