from django.contrib import admin

from activities.models import Activity, Grade


class GradeInline(admin.TabularInline):
    model = Grade

class ActivityAdmin(admin.ModelAdmin):
    inlines = [
        GradeInline,
    ]

admin.site.register(Activity, ActivityAdmin)
