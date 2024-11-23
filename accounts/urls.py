from django.urls import path 
from . import views 

app_name='accounts'

urlpatterns=[
    path('userRegister/',views.userRegister,name='userRegister'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('myAccount/',views.myAccount,name='myAccount'),
    path('activate/<uid>/<token>/',views.activate,name='activate'),
    path('customerDashboard/',views.customerDashboard,name='customerDashboard'),

    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('password_reset/<uid>/<token>/',views.password_reset,name='password_reset'),
    path('password_reset_done/',views.password_reset_done,name='password_reset_done'),


]