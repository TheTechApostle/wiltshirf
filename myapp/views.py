from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.http import JsonResponse
from django.db.models import Count, Prefetch
from .forms import *
from django.forms import modelformset_factory
from django.contrib import messages
from collections import OrderedDict
from django.conf import settings
import requests
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
import json
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .utils import *
from django.contrib.sessions.models import Session
from django.db.models import Sum, Count
from datetime import datetime
from django.db.models import Q
import csv
from .utils import is_admin, is_client
# Create your views here.


def myHome(request):
    getSlider = SliderImages.objects.all()
    getAgent = Agent.objects.all()
    getPropertyType = PropertyType.objects.distinct()
    ClientTestimonies = ClientTestimony.objects.all()
    getPropertyCount = PropertyType.objects.annotate(property_count=Count('property'))
    getPropertyLocation = Location.objects.all().distinct()

    # Group by property_type (ForeignKey), get distinct types
    property_types = PropertyType.objects.all()

    grouped_properties = OrderedDict()
    for prop_type in property_types:
        grouped_properties[prop_type.name] = Property.objects.filter(
            property_type=prop_type
        ).prefetch_related(
            Prefetch('images', queryset=PropertyImage.objects.all())
        )

    context = {
        'getSliders': getSlider,
        'ClientTestimonies': ClientTestimonies,
        'getPropertyLocation': getPropertyLocation,
        'getPropertyType': getPropertyCount,
        'getPropertyType_': getPropertyType,
        'grouped_properties': grouped_properties,
        'property_types': property_types,
        'getAgent': getAgent
    }

    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')


@login_required(login_url='LoginUser')  # Ensure the login URL name is correct
def createSlider(request):
    if request.method == "POST":
        text = request.POST.get('sliderText')
        slider = request.FILES.get('sliderImage')
        if text and slider:
            SliderImages.objects.create(sliderText=text, sliderImage=slider)
            return JsonResponse({'status': 'success', 'message': 'Slider Image Uploaded Successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing data'})
    return render(request, 'createSlider.html')


@login_required(login_url='LoginUser')  # Ensure the login URL name is correct
def propertyList(request):
    # Get all properties
    property_list = Property.objects.distinct().order_by('-date_added')

    # Pagination (6 per page)
    paginator = Paginator(property_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Total number of all properties
    total_property_count = Property.objects.count()

    # Group by location (change to 'country' if needed)
    country_property_count = Property.objects.values('location').annotate(total=Count('id')).order_by('-total')

    # Transactions (optional)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'page_obj': page_obj,
        'total_property_count': total_property_count,
        'country_property_count': country_property_count,
        'transactions': transactions,
    }
    return render(request, 'Dashboard/property_list.html', context)

     

@login_required(login_url='LoginUser')
def Dashboard(request):
    Google_API_KEY = 'AIzaSyDQUDUVxVx_y7t5JvAHfVC_hYpgsHlU8Io'
    user = request.user
    userFirstname = user.first_name
    is_client_user = is_client(user)
    is_admin_user = is_admin(user)

    # Initialize default values
    total_investment = 0
    to_balance = 0
    payment_progress = 0
    total_visitors = 0
    property_count = 0
    properties = Property.objects.none()  # Default empty queryset

    if is_admin_user:
        recent_payments = Transaction.objects.all().order_by('-created_at')[:5]  # Fetch latest 5
        full_payment_history_url = reverse('payment_history')
        # Admin sees all properties
        properties = Property.objects.all().order_by('-date_added')[:7]
        property_count = properties.count()
        
        # Sum deposits and outstanding balances across all purchases
        total_investment = PurchasedProduct.objects.aggregate(total=Sum('deposit'))['total'] or 0
        to_balance = PurchasedProduct.objects.aggregate(total=Sum('to_balance'))['total'] or 0

        # Count active sessions (as proxy for visitors)
        total_visitors = Session.objects.filter(expire_date__gte=datetime.now()).count()

    elif is_client_user:
        # Transaction History
        recent_payments = Transaction.objects.filter(user=user).order_by('-created_at')[:5]  # Fetch latest 5
        full_payment_history_url = reverse('payment_history')  # Define this URL in urls.py
        # Client sees only their purchased property titles
        purchased_titles = PurchasedProduct.objects.filter(user=user).values_list('title', flat=True)

        # Filter Property based on titles
        properties = Property.objects.prefetch_related('images').filter(title__in=purchased_titles).order_by('-date_added')[:5]
        property_count = properties.count()

        # Calculate investment and balance for this user
        total_investment = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('deposit'))['total'] or 0
        to_balance = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('to_balance'))['total'] or 0
        total_price = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('price'))['total'] or 0

        # Calculate payment progress percentage
        if total_price and total_price > 0:
            payment_progress = round((total_investment / total_price) * 100, 2)

    # Fetch user's transactions (if any)
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    # Context passed to the template
    context = {
        'recent_payments': recent_payments,
        'full_payment_history_url': full_payment_history_url,
        'property': properties,
        'GoogleAPIKEY':Google_API_KEY,
        'propertyCount': property_count,
        'user': user,
        'userFirstname': userFirstname,
        'is_client': is_client_user,
        'is_admin': is_admin_user,
        'total_investment': total_investment,
        'to_balance': to_balance,
        'payment_progress': payment_progress,
        'total_visitors': total_visitors,
        'transactions': transactions,
    }

    return render(request, 'Dashboard/index.html', context)


@login_required
def payment_history(request):
    user = request.user
    is_client_user = is_client(user)
    is_admin_user = is_admin(user)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    queryset = Transaction.objects.all().order_by('-created_at') if is_admin_user else Transaction.objects.filter(user=user).order_by('-created_at')

    if status_filter:
        queryset = queryset.filter(status__iexact=status_filter)

    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=payment_history.csv'
        writer = csv.writer(response)
        writer.writerow(['Amount', 'Payment Type', 'Status', 'Reference', 'Date'])

        for t in queryset:
            writer.writerow([
                t.amount,
                t.user or '-',
                t.status,
                t.reference or '-',
                t.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response

    context = {
        'all_payments': queryset,
        'payment_count': queryset.count(),
        'is_admin': is_admin_user,
        'is_client': is_client_user,
        'status_filter': status_filter,
    }
    return render(request, 'Dashboard/payment_history.html', context)


@login_required(login_url='LoginUser')  # Ensure the login URL name is correct
def propertyList(request):
    # Get all properties
    user= request.user
    property_list = Property.objects.distinct().order_by('-date_added').prefetch_related('images')
    userFirstname =  user.first_name
    if not is_admin(user):
        return HttpResponseForbidden("Access Denied: Only admin can access this page.")
    # Pagination (6 per page)
    paginator = Paginator(property_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Total number of all properties
    total_property_count = Property.objects.count()

    # Group by location (change to 'country' if needed)
    country_property_count = Property.objects.values('location').annotate(total=Count('id')).order_by('-total')

    # Transactions (optional)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'page_obj': page_obj,
        'total_property_count': total_property_count,
        'country_property_count': country_property_count,
        'transactions': transactions,
        'is_admin':True, 'user':user, 'userFirstname':userFirstname,
    }
    return render(request, 'Dashboard/property_list.html', context)

def FormProperty(request):
    ImageFormSet = modelformset_factory(PropertyImage, form=PropertyImageForm, extra=4, can_delete=False)

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=PropertyImage.objects.none())

        if form.is_valid() and formset.is_valid():
            prop = form.save()
            for image_form in formset:
                if image_form.cleaned_data.get('image') and image_form.cleaned_data.get('label'):
                    PropertyImage.objects.create(
                        property=prop,
                        image=image_form.cleaned_data['image'],
                        label=image_form.cleaned_data['label']
                    )
            messages.success(request, "Property created successfully!")
            return redirect('FormProperty')  # Redirect back to the same form or another page
    else:
        form = PropertyForm()
        formset = ImageFormSet(queryset=PropertyImage.objects.none())

    return render(request, 'Dashboard/property.html', {
        'form': form,
        'image_forms': formset
    })

def propertyType(request):
    listPropertyType = propertyType.objects.unique()
    if request.method == 'POST':
        FormProperty = PropertyTypeForm(request.POST)

        if FormProperty.is_valid():
            FormProperty.save()
            messages.success(request, 'Property Type Inserted Successfully')
            return redirect('propertyType')
    else:
        FormProperty = PropertyTypeForm()
        getPropertyType =  PropertyType.objects.all()
    context = {'FormProperty': FormProperty, 'property-type':getPropertyType, 'listPropertyType':listPropertyType}
    return render(request, 'Dashboard/propertyType.html',context )


def property_list(request):
    properties = property.objects.prefetch_related('images').all()
    return render(request, 'Dashboard/property_list.html', {'propertyView':properties})


# form Property Type

def FormPropertyType(request):
    formPropertyType = PropertyTypeForm(request.POST)
    if formPropertyType.is_valid():
        type_name = formPropertyType.cleaned_data['name'].strip().lower()

        # Check if it already exists (case-insensitive)
        checkProperty = PropertyType.objects.filter(name__iexact=type_name).exists()
        if checkProperty:
            messages.warning(request, f"Property Type '{type_name}' already exists.")
        else:
            formPropertyType.save()
            messages.success(request, 'Property Type Inserted Successfully')
            return redirect('/Dashboard/propertyType')
    return render(request, 'Dashboard/propertyType.html', {'property_type_form':formPropertyType})

# form Property Type

def FormPropertyLocation(request):
    formPropertyLocation = PropertyLocationForm(request.POST)
    if formPropertyLocation.is_valid():
        formPropertyLocation.save()
        messages.success(request, 'Property Location Inserted Successfully')
        return redirect('/Dashboard/propertyLocation')
    else:

        formPropertyLocation = PropertyLocationForm()
        
    return render(request, 'Dashboard/propertyLocation.html', {'property_location_form':formPropertyLocation})



def agent_list(request):
    agents = Agent.objects.all()
    return render(request, 'agents/agent_list.html', {'agents': agents})

def add_agent(request):
    if request.method == 'POST':
        form = AgentForm(request.POST, request.FILES)
        if form.is_valid():
            type_name = form.cleaned_data['name'].strip().lower()
            AgentProperty = Agent.objects.filter(name__iexact=type_name).exists()
            if AgentProperty:
                messages.warning(request, f"Agent Info '{type_name}' already exists.")
            else:
                form.save()
                messages.success(request, 'Agent added successfully.')
                
                return redirect('/Dashboard/add_agent')
    else:
        form = AgentForm()    
                
    return render(request, 'Dashboard/agent_form.html', {'form': form})


def clientTestimony(request):
    if request.method == 'POST':
        form = ClientTestimonyForm(request.POST, request.FILES)
        if form.is_valid():
            type_name = form.cleaned_data['name'].strip().lower()
            ClientTest = ClientTestimony.objects.filter(name__iexact=type_name).exists()
            if ClientTest:
                messages.warning(request, f"Client Testimony Info '{type_name}' already exists.")
            else:
                form.save()
                messages.success(request, 'Client Testimony added successfully.')
                
                return redirect('/Dashboard/client_testimony')
    else:
        form = ClientTestimonyForm()    
                
    return render(request, 'Dashboard/client_testimony.html', {'form': form})


def get_cordinate(address):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response =  requests.get(url)
    data =  response.json()
    if data['status']=='OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None


def viewProperty(request, id):
    getPropertyView = get_object_or_404(Property, id=id)
    images =  getPropertyView.images.all()
    address = getPropertyView.location
    lat, lng = get_cordinate(address)
    subscriptionPlan =  getPropertyView.subscription_plans.all()

    context = {
        'property':getPropertyView,
        'images':images,
        'lat':lat,
        'lng':lng,
        'google_maps_api_key':settings.GOOGLE_MAPS_API_KEY,
        'subscriptionPlan':subscriptionPlan
    }
    return render(request, 'viewProperty.html', context)


# registration
def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data['password'])
            user.save()

            # add to client group
            client_group, created =  Group.objects.get_or_create(name='client')
            user.groups.add(client_group)
            # Save profile
            ClientProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            messages.success(request, 'Account created successfully.')
            return redirect('LoginUser')
    else:
        form = ClientRegistrationForm()
    return render(request, 'register_client.html', {'form': form})

def LoginUser(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == "POST":
        form =  LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # validate by next_url
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)   
            return redirect("Dashboard")
        else:
            messages.warning(request, 'Authentication Failed..., Username or Password Error')
            context = {'form':form, 'next': next_url}
            return render(request, 'login.html', context)
    else:
        form = LoginForm()
        context = {'form': form}
        return render(request, 'login.html', context)
    

# logout view
def custom_logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, 'you have successfully logout')
    return redirect('LoginUser')


@login_required(login_url='LoginUser')  # Ensure the login URL name is correct
@require_POST
def add_to_cart(request, id):
    property_item = get_object_or_404(Property, id=id)
    cart = request.session.get('cart', {})

    if str(id) in cart:
        return JsonResponse({'message': 'This Property is already in your cart'}, status=200)

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            percentage = body.get('percentage', 100)
            deposit = body.get('deposit', 0)

            cart[str(id)] = {
                'title': property_item.title,
                'price': str(property_item.price),
                'initial_deposit_percent': percentage,
                'initial_deposit_amount': deposit,
                'image': property_item.images.first().image.url if property_item.images.exists() else ''
            }

            request.session['cart'] = cart
            request.session.modified = True

            return JsonResponse({'message': 'Property added to your cart'}, status=201)

        except Exception as e:
            return JsonResponse({'message': 'Error processing cart item'}, status=400)

    return JsonResponse({'message': 'Invalid request'}, status=405)


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})

    total_price = 0
    total_deposit = 0
    has_explicit_deposit = False

    for item in cart.values():
        price = float(item.get('price', 0))
        deposit = float(item.get('initial_deposit_amount', 0)) if item.get('initial_deposit_amount') else price

        total_price += price
        total_deposit += deposit

        # Check if the user explicitly selected a deposit option
        if item.get('initial_deposit_amount'):
            has_explicit_deposit = True

    context = {
        'cart': cart,
        'total_price': total_price,
        'total_deposit': total_deposit if has_explicit_deposit else None,
        'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
    }

    return render(request, 'cart.html', context)



@login_required
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    if id in cart:
        del cart[id]
        request.session['cart'] = cart
        request.session.modified = True
    return HttpResponseRedirect(reverse('view_cart'))


def add_subscription_plan(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if property.allSubscription != 'Yes':
        messages.error(request, "This property does not support subscription plans.")
        return redirect('viewProperty', id=property.id)

    if request.method == 'POST':
        form = SubscriptionPropertyPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.property = property

            # Do calculations here
            total_price = property.price
            deposit_percent = plan.initial_deposit_percent

            # Calculate initial payment
            initial_payment = total_price * Decimal(deposit_percent / 100)
            plan.initial_payment = initial_payment

            # Calculate monthly payment
            if plan.duration_months > 1:
                remaining = total_price - initial_payment
                months_remaining = plan.duration_months
                plan.monthly_payment = remaining / Decimal(months_remaining)
            else:
                plan.monthly_payment = Decimal("0.00")

            plan.save()
            messages.success(request, "Subscription plan added successfully.")
            return redirect('viewProperty', id=property.id)
    else:
        form = SubscriptionPropertyPlanForm()

    

    return render(request, 'Dashboard/add_plan.html', {'form': form, 'property': property})


def payment_success(request):
    reference = request.GET.get('reference')
    # Optionally verify with Paystack API here using secret key
    messages.success(request, "Payment successful! Reference: ", reference)
    return render(request, 'some_thank_you_page_or_dashboard.html')



@login_required
def verify_payment(request):
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, "No reference supplied.")
        return redirect('view_cart')

    # Check if transaction already exists
    if Transaction.objects.filter(reference=reference).exists():
        messages.success(request, "Transaction already verified.")
        return redirect('paymentVerification', reference=reference)

    # Verify with Paystack
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get('status') and res_data['data']['status'] == 'success':
        amount = res_data['data']['amount'] / 100  # Convert back to Naira

        # Save transaction
        transaction = Transaction.objects.create(
            user=request.user,
            reference=reference,
            amount=amount,
            status='success'
        )

        # Save purchased products
        cart_items = request.session.get('cart', {})
        for item in cart_items.values():
            price=float(item['price'])
            deposit=float(item.get('initial_deposit_amount', item['price']))
            to_balance = price - deposit
            PurchasedProduct.objects.create(
                user = request.user,
                transaction=transaction,
                title=item['title'],
                price=price,
                deposit=deposit,
                to_balance = to_balance
            )

        # Optional: Send email
        send_mail(
            subject="Payment Successful",
            message=f"Hi {request.user.username}, your payment of ₦{amount} was successful.\nReference: {reference}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True
        )

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f"Payment successful! Ref: {reference}")
        return redirect('paymentVerification', reference=reference)

    else:
        messages.error(request, "Payment verification failed.")
        return redirect('view_cart')
    
@login_required
def paymentVerification(request, reference):
    transaction = get_object_or_404(Transaction, reference=reference)
    products = transaction.products.all()  # using related_name from the model

    context = {
        'transaction': transaction,
        'products': products,
    }
    return render(request, 'Dashboard/payementVerification.html', context)




@login_required
def my_orders(request):
    user = request.user
    username = user.username
    is_client_user = is_client(user)
    orders = PurchasedProduct.objects.filter(user=request.user).order_by('-date_added')
    
    return render(request, 'Dashboard/my_orders.html', {'orders': orders, 'is_client':is_client_user, 'user_username':username})