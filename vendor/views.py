from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import User ,UserProfile
from accounts.forms import UserForm
from .forms import VendorForm
from django.template.defaultfilters  import slugify
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from accounts.utils import send_verification_email
from accounts.views import check_vendor
from accounts.forms import UserProfileForm
from .models import Vendor
from menu.models import Category,FoodItem
from menu.forms import CategoryForm,FoodItemForm
from urllib.parse import urlparse
from .forms import OpeningHourForm
from .models import OpeningHour
from django.http import JsonResponse 
from django.db import IntegrityError
from order.models import Order,OrderedFood
import datetime 


# Create your views here.

def get_vendor(request):
    vendor=Vendor.objects.get(user=request.user)
    return vendor 

@login_required(login_url='accounts:login')
@user_passes_test(check_vendor)
def vendorDashboard(request):
    vendor=Vendor.objects.get(user=request.user)
    orders=Order.objects.filter(vendors__in=[vendor.id],is_ordered=True).order_by('created_at')
    recent_orders=orders[:10]
    # Current month's revenue

    current_month=datetime.datetime.now().month
    current_month_orders=orders.filter(vendors__in=[vendor.id],created_at__month=current_month)
    current_month_revenue=0
    for i  in current_month_orders:
         current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    #total revenue
    total_revenue=0
    for i in orders:
        total_revenue+=i.get_total_by_vendor()['grand_total']

    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'total_revenue':total_revenue,
        'current_month_revenue':current_month_revenue,
    }


    return render(request,'vendor/vendorDashboard.html',context)


def vendorRegister(request):
    
    if request.method=='POST':
        form=UserForm(request.POST)
        v_form=VendorForm(request.POST,request.FILES)
        if form.is_valid() and v_form.is_valid():
            email=request.POST['email']
            username=request.POST['username']
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            phone_number=request.POST['phone_number']
            password=request.POST['password']
            user=User.objects.create_user(email=email,username=username,first_name=first_name,last_name=last_name,phone_number=phone_number,password=password)
            user.role=User.RESTAURANT
            user.save()
            mail_subject='please click to activate your account'
            mail_template='accounts/account_verification.html'
            send_verification_email(request,user,mail_subject,mail_template)
            
            vendor=v_form.save(commit=False)
            vendor.user=user
            userprofile=UserProfile.objects.get(user=user)
            vendor.user_profile=userprofile
            vendor.vendor_slug=slugify(vendor.vendor_name)+'-'+str(user.id)
            vendor.save()
            
            messages.success(request,'vendor register successfully')
            return redirect('accounts:login')
            
        else:
            return render(request,'vendor/vendorRegister.html',{'form':form,'v_form':v_form})

     
     
    else:
       uform=UserForm()
       vform=VendorForm()
       context={
          'form':uform,
          'v_form':vform
       }
       return render(request,'vendor/vendorRegister.html',context) 
    
@login_required(login_url='accounts:login')
@user_passes_test(check_vendor)
def vprofile(request):
    vendor=get_object_or_404(Vendor,user=request.user)
    profile=get_object_or_404(UserProfile,user=request.user)
    if request.method=='POST':
        user_profile=UserProfileForm(request.POST,request.FILES,instance=profile)
        vendor_profile=VendorForm(request.POST,request.FILES,instance=vendor)

        if user_profile.is_valid() and vendor_profile.is_valid():
            user_profile.save()
            vendor_profile.save()
            messages.success(request,'Setting updated successfully')
            return redirect('vendor:vprofile')
        else:
            context={
                'user_profile':user_profile,
                'vendor_profile':vendor_profile,
                'vendor':vendor,
                'profile':profile
            }
            messages.error(request,'Form not updated')
            return render(request,'vendor/vprofile.html',context)

    else:
     user_profile=UserProfileForm(instance=profile)
     vendor_profile=VendorForm(instance=vendor)
     context={
        'user_profile':user_profile,
        'vendor_profile':vendor_profile,
        'vendor':vendor,
        'profile':profile
     }
     return render(request,'vendor/vprofile.html',context) 
    
@login_required(login_url='accounts:login')
@user_passes_test(check_vendor)
def menu_builder(request):
    vendor=get_vendor(request)
    categories=Category.objects.filter(vendor=vendor)
    context={
        'categories':categories
    }
    return render(request,'vendor/menu_builder.html',context)

@login_required(login_url='accounts:login')
@user_passes_test(check_vendor)
def add_category(request):
    
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            category=form.save(commit=False)
            category.vendor=get_vendor(request)
            category_name=form.cleaned_data['category_name']
            category.slug=slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request,'Category Added')
            return redirect('vendor:menu_builder')
        else:    
            return render(request,'vendor/add_category.html',{'form':form})
    else:
        form=CategoryForm()
        context={
            'form':form
        }     
    

    return render(request,'vendor/add_category.html',context)

def food_items_by_category(request,pk):
    print(request.build_absolute_uri())
    vendor=get_vendor(request)
    category=get_object_or_404(Category,pk=pk)
    fooditems=FoodItem.objects.filter(vendor=vendor,category=category)
    context={
        'fooditems':fooditems,
        'category':category
    }
    return render(request,'vendor/food_items_by_category.html',context)
     

def edit_category(request,pk):
    category=get_object_or_404(Category,pk=pk)

    if request.method=='POST':
        form=CategoryForm(request.POST,instance=category)
        if form.is_valid():
            category_name=form.cleaned_data['category_name']
            category=form.save(commit=False)
            category.vendor=get_vendor(request)
            category.slug=slugify(category_name)
            category.save()
            messages.success(request,'Your Category has been updated')
            return redirect('vendor:menu_builder')
             
        else:
            return render(request,'vendor/edit_category.html',{'form':form})
    else:
        form=CategoryForm(instance=category)
        return render(request,'vendor/edit_category.html',{'form':form}) 


    
def delete_category(request,pk):
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category deleted')
    return redirect('vendor:menu_builder')
    

def add_food(request):
    
    # print(request.build_absolute_uri())
    if request.method=='POST':
        form=FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            foodtitle=form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor=get_vendor(request)
            food.slug=slugify(foodtitle)
            food.save()
            messages.success(request,'Food items has updated succesfully')
            return redirect('vendor:food_items_by_category' ,food.category.id)
        else:
            return render(request,'vendor/add_food.html',{'form':form})
    else:
        
      form=FoodItemForm()
      referrer_url = request.META.get('HTTP_REFERER', None)
      if referrer_url is not None:
         if "/menu_builder/food_items_by_category/" in referrer_url: 
          parsed_url=urlparse(referrer_url)
          print(parsed_url)
          path=parsed_url.path
          print(path)
          segments=path.strip("/").split("/")
          print(segments[-1])
          category=Category.objects.get(id=segments[-1])
          form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request),id=category.id)
          return render(request,'vendor/add_food.html',{'form':form})
        
                

          
      
      form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    return render(request,'vendor/add_food.html',{'form':form})

def edit_food(request,pk):
    food=get_object_or_404(FoodItem,pk=pk)
    if request.method=='POST':
        form=FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            foodtitle=form.cleaned_data['food_title']
            food1=form.save(commit=False)
            food1.vendor=get_vendor(request)
            food1.slug=slugify(foodtitle)
            food.save()
            messages.success(request,'Food items saved successfully')
            return redirect('vendor:food_items_by_category',food.category.id)
        else:
            return render(request,'vendor/edit_form.html',{'form':form,'food':food})
    else:
        form=FoodItemForm(instance=food)
    return render(request,'vendor/edit_food.html',{'form':form,'food':food})


def delete_food(request,pk):
    food=FoodItem.objects.get(pk=pk)
    food.delete()
    messages.success(request,'food items deleted successfuly')
    return redirect('vendor:food_items_by_category',food.category.id)    

def opening_hours(request):
    form=OpeningHourForm()
    opening_hours=OpeningHour.objects.filter(vendor=get_vendor(request))
    context={
        'form':form,
        'opening_hours':opening_hours
    }

    return render(request,'vendor/opening_hours.html',context)
    
def add_opening_hour(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status':'Failed','message':'user should be authenticated'})
    
    if request.headers.get('x-requested-with')!='XMLHttpRequest':
        return JsonResponse({'status':'Failed','message':'Invalid Request'})
    
    day=request.POST['day']
    from_hour=request.POST['from_hour']
    to_hour=request.POST['to_hour']
    is_closed=request.POST['is_closed']
    

    try:
        hour=OpeningHour.objects.create(vendor=get_vendor(request),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed)

        if hour:
            day=OpeningHour.objects.get(id=hour.id)
            if day.is_closed:
                
                response={'status':'success','id':hour.id,'day':day.get_day_display(),'is_closed':'closed'}
            else:
                
                response={'status':'success','id':hour.id,'day':day.get_day_display(),'from_hour':day.from_hour,'to_hour':day.to_hour}
            
            
            return JsonResponse(response)    
 
    except IntegrityError as e:
        response={'status':'Failed','message':from_hour+'-'+to_hour+'already exists','error':str(e)}

def remove_opening_hour(request,pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with')=='XMLHttpRequest':
            hour=get_object_or_404(OpeningHour,pk=pk)
            hour.delete()
            return JsonResponse({'status':'success','id':pk})
        

def order_detail(request,order_number):
    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        print(order)
        ordered_food=OrderedFood.objects.filter(order=order,fooditem__vendor=get_vendor(request))
        context={
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':order.get_total_by_vendor()['subtotal'],
            'tax_data':order.get_total_by_vendor()['tax_dict'],
            'grand_total':order.get_total_by_vendor()['grand_total'],


        }
    except:
        return render('vendor:vendorDashboard')    
    return render(request,'vendor/order_detail.html',context)


def my_orders(request):
    vendor=Vendor.objects.get(user=request.user)
    orders=Order.objects.filter(vendors__in=[vendor.id],is_ordered=True).order_by('created_at')
    context={
        'orders':orders
    }
    return render(request,'vendor/my_orders.html',context)



    
    
    
    