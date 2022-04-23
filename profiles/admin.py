from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
# from django.contrib.gis.forms import OpenLayersWidget # in case I want to change the GISModelAdmin gis_widget attribute which is OSMWidget by default
from django.contrib.auth.admin import UserAdmin

from profiles.models import CustomUser, Profile
from profiles.forms import CustomUserCreationForm, CustomUserForm


class CustomUserAdmin(UserAdmin):
    """Small customisation to adapt the CustomUser model to the admin_site"""
    add_form = CustomUserCreationForm
    form = CustomUserForm
    list_display = ('username', 'email', 'is_profile', 'date_joined', 'last_login', 'inactivity_email_sent')
    list_editable = ['email']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'language')}),
        (_('Permissions'), {'fields': ('is_active', 'is_profile', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Inactivity email sent'), {'fields': ['inactivity_email_sent']}),
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


class ProfileAdmin(GISModelAdmin):
    # gis_widget = OpenLayersWidget # OSMWidget is the default value but I added this line anyway if one day I want to change it to OpenLayersWidget with another base layer thanks to the template_name attribute.
    list_display = ('username', 'email', 'first_name', 'age', 'public_profile', 
                    'loggedin_less_than_12_month_ago', 'last_login',
                    'updated_less_than_12_month_ago', 'last_update',)
    list_display_links = ['username']
    readonly_fields = ['age','last_update']
    actions = GISModelAdmin.actions + [delete_profile_cleanly]

    class Meta:
        model = Profile

    def email(self, obj):
        return obj.user.email
    email.admin_order_field  = 'user__email'  #Allows column order sorting
    email.short_description = _('Email')  #Renames column head

    def username(self, obj):
        return obj.user.username
    username.admin_order_field  = 'user__username'  #Allows column order sorting
    username.short_description = _('Username')  #Renames column head

    def first_name(self, obj):
        return obj.user.first_name
    first_name.admin_order_field  = 'user__first_name'  #Allows column order sorting
    first_name.short_description = _('First name')  #Renames column head

    def last_login(self, obj):
        return obj.user.last_login
    last_login.admin_order_field  = 'user__last_login'  #Allows column order sorting
    last_login.short_description = _('Last login')  #Renames column head


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
