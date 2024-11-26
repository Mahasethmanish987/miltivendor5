from django.shortcuts import render,get_object_or_404,redirect
from vendor.models import Vendor,OpeningHour
from menu.models import Category,FoodItem
from django.db.models import Prefetch
from .models import Cart
from django.http import JsonResponse
from .context_processor import get_cart_counter,get_cart_amount
from django.db.models import Q
from accounts.models import UserProfile

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance 
from datetime import date ,datetime 
from order.forms import OrderForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def marketplace(request):
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)
    vendor_count=vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request,'marketplace/listing.html',context)

def vendor_detail(request,vendor_slug):
    vendor_instance=get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories=Category.objects.filter(vendor=vendor_instance).prefetch_related(
        Prefetch('fooditem_set',queryset=FoodItem.objects.filter(is_available=True))
    )
    opening_hours=OpeningHour.objects.filter(vendor=vendor_instance).order_by('day','from_hour')
    today=date.today()
    today=today.isoweekday()
    current_opening_hours=OpeningHour.objects.filter(vendor=vendor_instance,day=today)
    cart_items=None
    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    

    context={
        'Vendor':vendor_instance,
        'categories':categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
    }
    return render(request,'marketplace/vendor_detail.html',context)

def add_to_cart(request,food_id):
    print(food_id)
    if not request.user.is_authenticated:
        return JsonResponse({'status':'login_required','message':'Please login in '})

    if request.headers.get('x-requested-with') !='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalid request'})

    try:
        
        fooditem=FoodItem.objects.get(id=food_id)
        
        try:
            cart=Cart.objects.get(user=request.user,fooditem=fooditem)
            cart.quantity+=1
            cart.save()
            message='cart items quantity increased'
            
        except Cart.DoesNotExist:
            cart=Cart.objects.create(user=request.user,fooditem=fooditem,quantity=1)
            message='cart item added to cart'

        response_data={
            'status':'success',
            'message':message,
            'get_cart_count':get_cart_counter(request),
            'quantity':cart.quantity,
            'cart_amount':get_cart_amount(request)

        }
        return JsonResponse(response_data)    


    except:
        return JsonResponse({'status':'Failed','message':'N0o such food item'})            
    
def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                try:
                    chkcart=Cart.objects.get(user=request.user,fooditem=fooditem)
                    if chkcart.quantity >1 :
                        chkcart.quantity-=1
                        chkcart.save()
                    else:
                        chkcart.delete() 
                        chkcart.quantity=0
                    return JsonResponse({'status':'Success','message':'cart-items decreased','get_cart_counter':get_cart_counter(request),'quantity':chkcart.quantity,'cart_amount':get_cart_amount(request)})       
                except:
                    return JsonResponse({'status':'Failed','message':'no such cartitems is available'})    

            except:
                return JsonResponse({'status':'Failed','message':'No such food items'})        

        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})    
    else:
        return JsonResponse({'status':'login_required','message':'login_required'})         






def cart(request):
    cart_items=Cart.objects.filter(user=request.user)
    context={
        'cart_items':cart_items
    }    
    return render(request,'marketplace/cart.html',context)

def delete_cart(request,id):
   

   if not request.user.is_authenticated:
       return JsonResponse({'status':'login_required','message':'User login required'}, status=403)
   if  request.headers.get('x-requested-with')!='XMLHttpRequest':
       
       return JsonResponse({'status':'Failed','message':'Invalid request'}, status=400)
   
   try:
       cart_item=get_object_or_404(Cart,user=request.user,id=id)
       cart_item.delete()
       return JsonResponse({'status':'success','message':'item deleted successfully','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amount(request)})
   except Exception as e :
       return JsonResponse({'status':'Failed','message':f'Error:{str(e)}'}, status=500)



def search(request):
    
    if request.method=='POST':
        address=request.POST['address']
        rest_name=request.POST['rest_name']
        lat=request.POST['lat']
        lng=request.POST['lng']
        radius=request.POST['radius']

        fetch_vendor_by_fooditems=FoodItem.objects.filter(food_title__icontains=rest_name,is_available=True).values_list('vendor',flat=True)
        
        vendors=Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems)|Q(vendor_name__icontains=rest_name,is_approved=True,user__is_active=True))
        
        if lat and lng  and radius:
            pnt=GEOSGeometry('POINT(%s %s)'%(lng,lat))
            vendors=Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems)|Q(vendor_name__icontains=rest_name,
                                          is_approved=True,
                                          user__is_active=True),
                                          user_profile__location__distance_lte=(pnt,D(km=radius))
                                          ).annotate(distance=Distance("user_profile__location",pnt)).order_by('distance')
            for v in vendors:
                v.kms=round(v.distance.km,1)
            
        
        vendor_count=vendors.count()
        context={
        'vendors':vendors,
        'vendor_count':vendor_count,
        'source_location':address,
    }
    return render(request,'marketplace/listing.html',context)


@login_required(login_url='accounts:login')        
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    user_profile=UserProfile.objects.get(user=request.user)
    if cart_count<=0:
        return redirect('marketplace:marketplace')
   
    default={'first_name':request.user.first_name,
             'last_name':request.user.last_name,
             'email':request.user.email,
             'phone':request.user.phone_number,
             'address':user_profile.address,
             'country':user_profile.country,
             'state':user_profile.state,
             'pin_code':user_profile.pin_code}
    form=OrderForm(initial=default)
    context={
        'form':form,
        'cart_items':cart_items
    }
    return render(request,'marketplace/checkout.html',context)


