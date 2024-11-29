from django.urls import path 
from . import views 

app_name='vendor'

urlpatterns=[
    path('',views.vendorDashboard,name='vendorDashboard'),
    path('vendorRegister/',views.vendorRegister,name='vendorRegister'),
    path('vprofile/',views.vprofile,name='vprofile'),

    #Category added
    path('menu_builder/',views.menu_builder,name='menu_builder'),
    path('menu_builder/food_items_by_category/<int:pk>',views.food_items_by_category,name='food_items_by_category'),

    path('menu_builder/category/add_category',views.add_category,name='add_category'),
    path('menu_builder/category/edit_category/<int:pk>/',views.edit_category,name='edit_category'),
    path('menu_builder/category/delete_category/<int:pk>/',views.delete_category,name='delete_category'),

    #FoodItem add
    path('menu_builder/food/add_food/',views.add_food,name='add_food'),
    path('menu_builder/food/edit_food/<int:pk>/',views.edit_food,name='edit_food'),
    path('menu_builder/food/delete_food/<int:pk>/',views.delete_food,name='delete_food'),

    path('opening_hours/',views.opening_hours,name='opening_hours'),
    path('opening_hours/add',views.add_opening_hour,name='add_opening_hour'),
    path('opening_hours/remove/<int:pk>/',views.remove_opening_hour,name='remove_opening_hour'),



    path('order_detail/<int:order_number>/',views.order_detail,name='vendor_order_detail'),
    path('my_orders/',views.my_orders,name='vendor_my_orders'),
    


]