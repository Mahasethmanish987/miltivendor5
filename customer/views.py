from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm,UserInfoForm
from accounts.models import UserProfile,User
from django.contrib import messages


# Create your views here.
@login_required(login_url='accounts:login')
def customerDashboard(request):
   
   return render(request,'customer/customerDashboard.html')

@login_required(login_url='accounts:login')
def cprofile(request):
    profile=get_object_or_404(UserProfile,user=request.user)
    

    if request.method=='POST':
        profile_form=UserProfileForm(request.POST,request.FILES,instance=profile)
        user_form=UserInfoForm(request.POST,instance=request.user)  
        if profile_form.is_valid() and user_form.is_valid():
           profile_form.save()
           user_form.save()
           messages.success(request,'Profile Updated')
           return redirect('customer:cprofile')
        else:
           return render(request,'customer/cprofile.html',{'profile_form':profile_form,'user_form':user_form})    
    else:
     profile_form=UserProfileForm(instance=profile)
     user_form=UserInfoForm(instance=request.user)
     context={
        'profile_form':profile_form,
        'user_form':user_form,
        'profile':profile,
        
    }
    return render(request,'customer/cprofile.html',context)
