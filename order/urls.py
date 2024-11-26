from django.urls import path 
from . import views 

app_name='order'
urlpatterns=[
    path('place_order/',views.place_order,name='place_order'),
    path('api/paypal/order/create/',views.create_order,name='create_order'),
    path('payments/',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    

]