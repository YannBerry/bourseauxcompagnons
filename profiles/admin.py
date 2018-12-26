from django.utils.translation import gettext_lazy as _
from django.contrib import admin
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


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['age']
    class Meta:
        model = Profile


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
