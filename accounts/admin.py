from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import (
    AdminUserChangeForm,
    AdminUserCreationForm,
)
from .models import Token


User = get_user_model()


class UserAdmin(BaseUserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    list_display = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_admin', 'is_superuser',
                    'date_joined', 'last_login', 'updated']
    list_display_links = list_display
    list_filter = ['date_joined', 'last_login', 'is_active', 'is_admin', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',  'first_name', 'last_name', 'phone_number', 'password1', 'password2',)
        }),
    )
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = ()


class TokenAdmin(admin.ModelAdmin):
    model = Token
    list_display = ['key', 'user', 'created', 'updated', 'logout']
    list_display_links = list_display
    search_fields = ['user__email', 'key']


admin.site.register(User, UserAdmin)
admin.site.register(Token, TokenAdmin)
