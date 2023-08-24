from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['inn', 'email', 'label', 'address', 'leader_name', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('inn', 'email', 'password')}),
        ('Personal Info', {'fields': ('label', 'address', 'leader_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('inn', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('inn', 'email', 'label', 'leader_name')
    ordering = ('inn',)

admin.site.register(CustomUser, CustomUserAdmin)
