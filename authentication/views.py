from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Customer
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password


def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('ph-no')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        password = request.POST.get('password')

    
        if not (full_name and email and phone_number and address and city and country and password):
            return render(request, 'html/signup.html', {'error': 'Fields are Empty'})
           
        
        if len(password) < 6:
            return render(request, 'html/signup.html', {'error': 'Password must be at least 8 characters long.'})
            
        
        if not phone_number.isdigit():
             return render(request, 'html/signup.html', {'error': 'Phone number must be a Digit'})
            

        if len(phone_number) < 10 or len(phone_number) > 15:
            return render(request, 'html/signup.html', {'error': 'Enter Valid Phone Number.'})
          
    
        # Check if email already exists
        if Customer.objects.filter(email=email).exists():
            return render(request, 'html/signup.html', {'error': 'Email Already Exists'})
        
        
        hashed_password = make_password(password)

    
        customer = Customer(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city=city,
            country=country,
            password=hashed_password  
        )
        customer.save()
        return render(request, 'html/login.html', {'success': 'Registration successful.'})
        
    return render(request,'html/signup.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                request.session['user_id'] = customer.id
                print("logged in successfully")
                return redirect('index')  
            else:
               print("Invalid email or password")
               return render(request, 'html/login.html', {'error': 'Invalid email or password'})
        except Customer.DoesNotExist:
            print("Invalid email or password.")
            return render(request, 'html/login.html', {'error': 'No User Found'})
             
    return render(request,'html/login.html')



