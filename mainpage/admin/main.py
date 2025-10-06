from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from ..models import CustomUser  # If this file is inside an admin/ folder
# If not inside an `admin/` folder, use:
# from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    # Fields shown on the change user page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Custom'), {'fields': ('role', 'organization')}),  # Your custom fields
    )

    # Fields shown when creating a new user in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'organization'),
        }),
    )

    # Fields to show in the user list
    list_display = ('username', 'email', 'role', 'organization', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
from ..models import staffInfo

@admin.register(staffInfo)
class StaffInfoAdmin(admin.ModelAdmin):
    list_display = (
        'staffID',
        'lastname',
        'firstname',
        'middlename',
        'sex',
        'emailadd',
        'contact',
        'extension',
    )
    search_fields = ('lastname', 'firstname', 'staffID')
    list_filter = ('sex',)
    ordering = ('staffID',)