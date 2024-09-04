from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['inn', 'label', 'address', 'representative_person', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('inn', 'ogrn', 'kpp')}),
        ('Персональная информация', {'fields': (
            'label',
            'address',
            'representative_person'
        )}),
        ('Файлы', {'fields': ('mkd', 'egrul')}),
        ('Доступы', {'fields': ('is_active', 'is_staff')}),
        ('Пароль', {'fields': ('password',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('inn', 'password1', 'password2'),
        }),
    )
    search_fields = ('inn', 'label', 'representative_person')
    ordering = ('inn',)


admin.site.register(CustomUser, CustomUserAdmin)
