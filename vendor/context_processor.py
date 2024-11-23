from .models import Vendor
from django.conf import settings
def get_vendor(request):
    
    try:

       vendor=Vendor.objects.get(user=request.user)
    except:
        vendor=None   
    return {'vendor':vendor}

def get_google_api(request):
    return {'GOOGLE_API_KEY':settings.GOOGLE_API_KEY}
    