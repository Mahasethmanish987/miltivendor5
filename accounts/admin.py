from django.contrib import admin
from .models import User,UserProfile
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=('email','username','is_active','role','last_login','modified_at')
    list_display_links=('email','username','last_login','modified_at')
    list_editable=('is_active',)
    readonly_fields=('password','role')
    ordering=('created_at',)
    list_filter=('role',)

admin.site.register(User,UserAdmin)
admin.site.register(UserProfile)