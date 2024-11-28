from django.urls import path 
from . import views 

app_name='customer'

urlpatterns=[
    path('',views.customerDashboard,name='customerDashboard'),
    path('profile/',views.cprofile,name='cprofile') ,
    path('my_orders/',views.my_orders,name='my_orders'),
    path('order_details/<int:order_number>/',views.order_detail,name='order_detail'),

]