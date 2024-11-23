from django.contrib import admin
from .models import Vendor,OpeningHour
# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display=('vendor_name','user__email','is_approved','created_at')
    list_editable=('is_approved',)
admin.site.register(Vendor,VendorAdmin)

admin.site.register(OpeningHour)