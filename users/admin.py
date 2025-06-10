from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'loma', 'is_staff')
    list_filter = ('loma', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('loma', 'talrunis', 'registracijas_datums')}),
    )
    readonly_fields = ('registracijas_datums',)

admin.site.register(User, CustomUserAdmin)