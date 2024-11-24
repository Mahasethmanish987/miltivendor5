from django.shortcuts import render,redirect
from .models import User,UserManager  
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .utils import detectUser,send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied 
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

def check_vendor(user):
    
    if user.role==1:
        return True 
    else:
        raise PermissionDenied
    
def check_customer(user):
    if user.role==2:
        return True
    else:
        raise PermissionDenied


def userRegister(request):
    if request.user.is_authenticated:
        messages.info(request,'user has been already loggedin')
        return redirect('myapp:index')
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            username=request.POST['username']
            phone_number=request.POST['phone_number']
            email=request.POST['email']
            password=request.POST['password']
            confirm_password=request.POST['confirm_password']
            user=User.objects.create_user(email=email,first_name=first_name,last_name=last_name,username=username,phone_number=phone_number,password=password)
            user.role=User.CUSTOMER
            user.save()
            mail_subject='Please activate your account'
            mail_template='accounts/account_verification.html'
            send_verification_email(request,user,mail_subject,mail_template)

            messages.success(request,'User registered successfully')
            return redirect('myapp:index')
        else:
            return render(request,'accounts/userRegister.html',{'form':form}) 
    else:
        form=UserForm()       
    return render(request,'accounts/userRegister.html',{'form':form})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request,'user has been already loggedin')
        return redirect('myapp:index')
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(email=email,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,'User has been successfully logged in ')
            return redirect('accounts:myAccount')
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('accounts:login')
    return render(request,'accounts/login.html')

def logout_view(request):
    if not request.user.is_authenticated:
        messages.info(request,'user has been already loggedout')
        return redirect('myapp:index')
    logout(request)
    messages.info(request,'You have been loggedout')
    return redirect('accounts:login')

@login_required(login_url='accounts:login')
def myAccount(request):
    user=request.user
    redirectUrl=detectUser(user)

    if redirectUrl=='admin:index':
        return redirect('admin:index')
    elif redirectUrl=='customerDashboard':
        return redirect('customer:customerDashboard')
    else:
        return redirect('vendor:vendorDashboard')
    


def activate(request,uid,token):
    try:
        id=urlsafe_base64_decode(uid).decode()
        user=User.objects.get(pk=id)
    except User.DoesNotExist:
        user=None 
    except (TypeError,ValueError,OverflowError):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.info(request,'User is successfully activated please login')
        return redirect('accounts:login')

    else:
        messages.error(request,'Invalid Link')
        return redirect('accounts:userRegister')



def forgot_password(request):

    if request.method=='POST':
        email=request.POST['email']
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            mail_subject='Please click the reset link to reset the password'
            mail_template='accounts/password_reset.html'
            send_verification_email(request,user,mail_subject,mail_template)
            messages.info(request,'Reset email has successfully send to Your email')
            return redirect('myapp:index')
        else:
            messages.info(request,'Please put the correct Email')
            return redirect('accounts:forgot_password')

    return render(request,'accounts/forgot_password.html')        


def password_reset(request,uid,token):
    try:
        pk=urlsafe_base64_decode(uid).decode()
        user=User.objects.get(pk=pk)
    except User.DoesNotExist:
        user=None
    except (TypeError,OverflowError,ValueError):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['pk']=pk
        messages.info(request,'Please reset your password')
        return redirect('accounts:password_reset_done')
    else:
        messages.info(request,'Invailid Link')
        return redirect('accounts:forgot_password')            


def password_reset_done(request):
    if request.method=='POST':
          password=request.POST['password']
          confirm_password=request.POST['confirm_password']
          if password !=confirm_password:
               messages.info(request,'password and confirm password does not match')
               return render(request,'accounts/password_reset_done.html')
          else:
                pk=request.session.get('pk')
                if pk is None:
                    messages.error(request,'User not found')
                    return redirect('accounts:forgot_password')
                try:
                    user=User.objects.get(pk=pk)
                except User.DoesNotExist:
                    messages.error(request,'User Not Found')
                    return redirect('accounts:forgot_password')
                user.set_password(password)
                user.is_active=True
                user.save()
                messages.success(request,'passwor reset successfully')
                return redirect('accounts:login')    
             
    return render(request,'accounts/password_reset_done.html')      
          




        
        





