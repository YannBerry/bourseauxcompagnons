from django.contrib import admin

from outings.models import Outing


class OutingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'start_date', 'end_date', 'author']
    search_fields = ['title']
    autocomplete_fields = ['author']

    class Meta:
        model = Outing

admin.site.register(Outing, OutingAdmin)