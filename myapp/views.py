from django.shortcuts import render
from django.contrib.gis.geos import Point 
from vendor.models import Vendor
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


# Create your views here.

def get_or_set_current_location(request):
  if 'lat' in request.session:
    lat=float(request.session['lat'])
    lng=float(request.session['lng'])
    return lng,lat 

  if 'lat' and 'lng' in request.GET:
         lat=float(request.GET.get('lat'))
         lng=float(request.GET.get('lng'))
         request.session['lat']=lat
         request.session['lng']=lng
         return lng , lat  
  else:
     return None

def index(request):

   if get_or_set_current_location(request):
        
        
        pnt=Point(get_or_set_current_location(request))
        vendors=Vendor.objects.filter(user_profile__location__distance_lte=(pnt,D(km=3))).annotate(distance=Distance("user_profile__location",pnt)).order_by('distance')
        for v in vendors:
            v.kms=round(v.distance.km,1)
   else:
       vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)[:7] 

   context={
       'vendors':vendors
   }
   print(vendors)            

    

   return render(request,'myapp/index.html',context)
