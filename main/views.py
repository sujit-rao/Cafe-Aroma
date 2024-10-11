from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.views.decorators.csrf import csrf_exempt
import razorpay
from .models import Order
from django.conf import settings
from authentication.models import Customer
from .models import Contact, Product
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import pkg_resources


def index(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        contact = Contact.objects.create(name=name, email=email, message=message)
        contact.save()
    
        subject = 'New Contact Message'
        message_body = f'You have received a new message from {name} ({email}):\n\n{message}'
        from_email = email  
        admin_emails = ['cafearoumaa@gmail.com'] 
        send_mail(subject, message_body, from_email, admin_emails)
        return redirect('/')
    return render(request, 'html/index.html')




def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            contact = Contact.objects.create(name=name, email=email, message=message)
            contact.save()
            subject = 'New Contact Message'
            message_body = f'You have received a new message from {name} ({email}):\n\n{message}'
            from_email = email
            admin_emails = ['cafearoumaa@gmail.com'] 
            send_mail(subject, message_body, from_email, admin_emails)
            return render(request, 'html/index.html', {'success': 'Message Sent!'})
        else:
            return render(request, 'html/contact.html', {'error': 'Oops! Message not Sent'})

    
    return render(request, 'html/contact.html')




def recipe(request):
    products = Product.objects.all()
   
    for product in products:
        if product.image:
            print(product.image.url)
    else:
        print("No image for product:", product.title)
    return render(request, 'html/recipe.html', {'products': products})
    

## Profile

def profile(request):
    user_id = request.session.get('user_id')
    if 'user_id' not in request.session:
        return redirect('login') 
    
    try:
        customer = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return redirect('login')
    
    return render(request, 'html/profile.html', {'customer': customer})


## User Transaction details view

def user_transactions(request):
    # Check if the user is authenticated
    user_id = request.session.get('user_id')
    if 'user_id' not in request.session:
        return render(request, 'html/login.html', {'error': 'No User Found, Login first '})
    try:
        customer = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return render(request, 'html/login.html', {'error': 'No User Found, Login first'})
    if customer:
            try:
                customer = Customer.objects.get(id=user_id)
                print(f"Debug: Customer {customer.full_name} with ID {customer.id} is logged in.")
                
                # Filter orders by this customer
                orders =  orders = Order.objects.filter(customer=customer, status='Completed').order_by('-order_date')
            except Customer.DoesNotExist:
                print("Debug: Customer does not exist for this user.")
                orders = []  # If the customer doesn't exist, return an empty list
            context = {
                'orders': orders
             }
            return render(request, 'html/transaction.html', context)
    else:
        return render('request', 'html/login.html')

## CART VIEWS
def cart(request):
    cart = request.session.get('cart', {})
    total_price = request.session.get('total_price', 0)
    
    return render(request, 'html/cart.html', {'cart':cart, 'total_price': total_price})



def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    
   
    
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        # Ensure quantity doesn't exceed 15
        current_quantity = cart[str(product_id)]['quantity']
        if current_quantity + quantity > 15:
            cart[str(product_id)]['quantity'] = 15  # Set it to max 15 if exceeded
        else:
            cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
        'title': product.title,
        'image_url': product.image.url,
        'description': product.description,
        'price': float(product.price),
        'quantity': quantity,
        'subtotal': float(product.price)* quantity
        }
    

    cart[str(product_id)]['subtotal'] = cart[str(product_id)]['price'] * cart[str(product_id)]['quantity']
    request.session['cart'] = cart
    total_price = sum(item['subtotal'] for item in cart.values())
    request.session['total_price'] = total_price

    return redirect('cart')  



def delete_from_cart(request, product_id):
   
    cart = request.session.get('cart', {})
    
   
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart

    total_price = sum(item['subtotal'] for item in cart.values())
    request.session['total_price'] = total_price
    
    
    request.session['cart'] = cart
    
    return redirect('cart') 



def logout_view(request):
    
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index') 

## ORDER VIEWS

def initiate_payment(request):
   
    user_id = request.session.get('user_id')
    if 'user_id' not in request.session:
        return render(request, 'html/cart.html', {'error': 'No User Found, Login first '})
    
    try:
        customer = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return render(request, 'html/cart.html', {'error': 'No User Found, Login first'})
    
    if customer:

        # Retrieve cart and calculate total price
        cart = request.session.get('cart', {})
        total_price = sum(item['subtotal'] for item in cart.values())

        # Create an order in the database
        order = Order.objects.create(
            customer=customer,
            total_price=total_price,
        )

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = client.order.create(dict(
            amount=int(total_price * 100),  # amount in paise
            currency='INR',
            payment_capture='1',
        ))

        # Save Razorpay order ID
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # Pass data to Razorpay checkout page
        context = {
            'order_id': razorpay_order['id'],
            'amount': total_price * 100,  # amount in paise
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'customer_name': customer.full_name,  # Add full name of the customer
            'customer_email': customer.email, 

        }
        return render(request, 'html/razorpay_checkout.html', context)
    else:
        return render(request, 'html/cart.html', {'error': 'Log in To Pay'}, context)


@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Retrieve the order from the database
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return HttpResponse('Order not found', status=404)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            order.status = 'Failed'
            order.save()
            return HttpResponse('Payment verification failed', status=400)

        # Update the order status
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = 'Completed'
        order.save()

        return render(request, 'html/success.html',{
            'customer_name':order.customer.full_name,  # Assuming you have this field in your Order model
            'payment_id': razorpay_payment_id
        })  # Redirect to a success page or confirmation page
    else:
        return HttpResponse('Invalid request', status=400)



def dev_page(request):
    return render(request, 'html/developer.html')