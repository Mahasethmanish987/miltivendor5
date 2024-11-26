from django.shortcuts import render,redirect
from marketplace.models import Cart
from marketplace.context_processor import get_cart_amount
from order.forms import OrderForm
from order.models import  Order,Payment
import json 
from decimal import Decimal 
from .utils import generate_order
import simplejson as json 
import requests
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import OrderedFood
from accounts.utils import send_notification
# Create your views here.

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # or str(obj)
        return super().default(obj)

def place_order(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('marketplace:marketplace')
    subtotal=get_cart_amount(request)['subtotal']
    total_tax=get_cart_amount(request)['tax']
    grand_total=get_cart_amount(request)['grand_total']
    tax_data=get_cart_amount(request)['tax_dict']
    

    if request.method=="POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            order=Order()
            order.first_name=form.cleaned_data['first_name']
            order.last_name=form.cleaned_data['last_name']
            order.phone=form.cleaned_data['phone']
            order.email=form.cleaned_data['email']
            order.address=form.cleaned_data['address']
            order.country=form.cleaned_data['country']
            order.state=form.cleaned_data['state']
            order.pin_code=form.cleaned_data['pin_code']
            order.user=request.user
            order.total=grand_total
            order.tax_data=json.dumps(tax_data,cls=DecimalEncoder)
            order.total_tax=total_tax
            order.payment_method=request.POST['payment_method']
            order.save()
            order.order_number=generate_order(request.user.id,order.id)
            order.save()
            context={
                'order':order,
                'cart_items':cart_items
            }
            return render(request,'order/place_order.html',context)

        else:
            print(form.errors)



    return render(request,'order/place_order.html')
@csrf_exempt
def create_order(request):
    PAYPAL_CLIENT_ID = 'AZX9UrVFCr_euz3bwcQ-Un32Ok5_r_7ax3sMyw4dnKlcfmvJ8zKOoYp93AGDn0HiGvefec8Ems1MljIC'
    PAYPAL_CLIENT_SECRET = 'EECFBpcUH1acr2reC6OqQx4_ee_v_gpRPzdtnITGW5GkCywSZ4_9MnRdZJl5QQCU7z88UMbA6P256-fk'
    PAYPAL_API_URL = 'https://api-m.sandbox.paypal.com'

    try:
        auth_response=requests.post(
            f"{PAYPAL_API_URL}/v1/oauth2/token",
            headers={'Accept':'application/json','Accept-Language':'en-us'},
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID,PAYPAL_CLIENT_SECRET),
            data={'grant_type':'client_credentials'}
        )
        auth_response.raise_for_status()
        access_token=auth_response.json().get('access_token')
        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": "100.00"  # Replace with your order total
                    }
                }
            ]
        }

        order_response = requests.post(
            f"{PAYPAL_API_URL}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=order_payload
        )
        order_response.raise_for_status()

        # Return the order ID to the frontend
        order_data = order_response.json()
        return JsonResponse({"id": order_data["id"]}, status=201)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def capture_order(request,order_id):
    PAYPAL_CLIENT_ID = 'AZX9UrVFCr_euz3bwcQ-Un32Ok5_r_7ax3sMyw4dnKlcfmvJ8zKOoYp93AGDn0HiGvefec8Ems1MljIC'
    PAYPAL_CLIENT_SECRET = 'EECFBpcUH1acr2reC6OqQx4_ee_v_gpRPzdtnITGW5GkCywSZ4_9MnRdZJl5QQCU7z88UMbA6P256-fk'
    PAYPAL_API_URL = 'https://api-m.sandbox.paypal.com'

    try:
        auth_response=requests.post(
            f"{PAYPAL_API_URL}/v1/oauth2/token",
            headers={'Accept':'application/json','Accept-Language':'en-us'},
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID,PAYPAL_CLIENT_SECRET),
            data={'grant_type':'client_credentials'}
        )
        auth_response.raise_for_status()
        access_token=auth_response.json().get('access_token')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(
            f"{PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture", headers=headers
        )
        
        response.raise_for_status()
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)    
    


def payments(request):

    if not request.user.is_authenticated:
        return JsonResponse({'status':'Failed','message':'User must be logged in'})

    if request.headers.get('x-requested-with')!='XMLHttpRequest' and request.method!='POST':
        return JsonResponse({'status':'failed','message':'invalid request'})

    order_number=request.POST.get('order_number')    
    transaction_id=request.POST.get('transaction_id')    
    payment_method=request.POST.get('payment_method')
    status=request.POST.get('status')
    

    order=Order.objects.get(user=request.user,order_number=order_number)
    payment=Payment(
        user=request.user,
        transaction_id=transaction_id,
        payment_method=payment_method,
        amount=order.total,
        status=status
    )
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()
     
    #Move the cart to ordered Food model 
    cart_items=Cart.objects.filter(user=request.user)
    for item in cart_items:
        ordered_food=OrderedFood()
        ordered_food.order=order
        ordered_food.payment=payment 
        ordered_food.user=request.user
        ordered_food.fooditem=item.fooditem
        ordered_food.quantity=item.quantity
        ordered_food.price=item.fooditem.price
        ordered_food.amount=item.fooditem .price *item.quantity
        ordered_food.save() 


    
    # send order confirmation email to the customer
    mail_subject='Thanks you for ordering with us.'
    mail_template='order/order_confirmation_email.html'
    context={
        'user_first_name':request.user.first_name ,

        'order_id':order.order_number,
        'order_transaction_id':order.payment.transaction_id,
        'to_email':order.email
        
    }
    send_notification.delay(mail_subject,mail_template,context)
    

    # send order received email to the vendor
    to_emails=[]
    for i in cart_items:
       if i.fooditem.vendor.user.email not in to_emails: 
        to_emails.append(i.fooditem.vendor.user.email)
    print(to_emails)    

    mail_subject='You have received a new order'
    mail_template='order/new_order_received.html'
    context={
        
        'to_email':to_emails,
    }
    send_notification.delay(mail_subject,mail_template,context)
    

    #clear the cart items 
    # cart_items.delete()

    response={
        'order_number':order_number,
        'transaction_id':transaction_id
    }
    return JsonResponse(response)
    

def order_complete(request):
    order_number=request.GET.get('order_no')
    transaction_id=request.GET.get('trans_id')
    try:
        order= Order.objects.get(order_number=order_number,payment__transaction_id=transaction_id,is_ordered=True)
        ordered_food= OrderedFood.objects.filter(order=order)
        subtotal=0  
        for item in ordered_food:
            subtotal+=(item.price * item.quantity)

        tax_data=json.loads(order.tax_data)

        context={
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data 
        }
        return render(request,'order/order_complete.html',context)

    except Order.DoesNotExist:
        print(f"Order with number {order_number} and transaction ID {transaction_id} not found.")
        return redirect('myapp:index')  # Redirect to the index view if order is not found
    except Exception as e:
        print(f"Unexpected error: {e}")
        return redirect('myapp:index')
    



    
