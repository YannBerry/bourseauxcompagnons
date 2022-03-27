from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin #subclass of GeoModelAdmin
from django.contrib.auth.admin import UserAdmin

from profiles.models import CustomUser, Profile
from profiles.forms import CustomUserCreationForm, CustomUserForm


class CustomUserAdmin(UserAdmin):
    """Small customisation to adapt the CustomUser model to the admin_site"""
    add_form = CustomUserCreationForm
    form = CustomUserForm
    list_display = ('username', 'email', 'is_staff', 'is_profile')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_profile', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

def delete_profile_cleanly(modeladmin, request, queryset):
    """When deleting a profile in the profiles admin page, the CustomUser is_profile attribute is set to False."""
    for obj in queryset:
        obj.user.is_profile = False
        obj.user.save()
        obj.delete()
delete_profile_cleanly.short_description = _("Delete selected profiles cleanly (user.is_profile=False)")

class ProfileAdmin(OSMGeoAdmin):
    list_display = ('email', 'first_name', 'birthdate')
    readonly_fields = ['age']
    # actions = [delete_profile_cleanly]
    actions = OSMGeoAdmin.actions + [delete_profile_cleanly]

    class Meta:
        model = Profile

    def email(self, obj):
        return obj.user.email
    email.admin_order_field  = 'user__email'  #Allows column order sorting
    email.short_description = _('Email')  #Renames column head

    def first_name(self, obj):
        return obj.user.first_name
    first_name.admin_order_field  = 'user__first_name'  #Allows column order sorting
    first_name.short_description = _('First name')  #Renames column head

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
