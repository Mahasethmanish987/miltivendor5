from django.contrib import admin
from .models import Payment,Order,OrderedFood

# Register your models here.
class OrderedFoodInline(admin.TabularInline):
    model=OrderedFood
    readonly_fields=('order','payment','user','fooditem','quantity','price','amount')
    extra=0
# class OrderInline(admin.TabularInline):
#     model=OrderedFood
#     extra=0

class paymentAdmin(admin.ModelAdmin):
    fields=('user','transaction_id','payment_method','status')
    inlines=[OrderedFoodInline]
       
    
class orderAdmin(admin.ModelAdmin):
    list_display=('order_number','name','phone','email','total','payment_method','order_placed_to','status')
    inlines=[OrderedFoodInline]

admin.site.register(Payment,paymentAdmin)
admin.site.register(Order,orderAdmin)
admin.site.register(OrderedFood)