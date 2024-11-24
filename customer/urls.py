from django.urls import path 
from . import views 

app_name='customer'

urlpatterns=[
    path('',views.customerDashboard,name='customerDashboard'),
    path('profile/',views.cprofile,name='cprofile') ,
]