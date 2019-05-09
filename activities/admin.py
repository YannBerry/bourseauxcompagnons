from django.contrib import admin

from activities.models import Activity, Grade

from modeltranslation.admin import TranslationAdmin


class GradeInline(admin.TabularInline):
    model = Grade

class ActivityAdmin(TranslationAdmin):
    inlines = [
        GradeInline,
    ]

admin.site.register(Activity, ActivityAdmin)
