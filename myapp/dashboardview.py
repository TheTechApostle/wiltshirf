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


@login_required(login_url="LoginUser")
def Dashboard(request):
    getDate = datetime.now().year
    user = request.user
    is_client_user = is_client(user)
    is_admin_user = is_admin(user)

    total_investment = 0
    to_balance = 0
    payment_progress = 0
    total_visitors = 0
    property_count = 0
    properties = Property.objects.none()
    recent_payments = 0

    if is_admin_user:
        recent_payments = Transaction.objects.all().order_by('-created_at')[:5]
        purchased_xCount = PurchasedProduct.objects.all().count()
        properties = Property.objects.all().order_by('-date_added')[:7]
        total_visitors = Session.objects.filter(expire_date__gte=datetime.now()).count()
        total_investment = PurchasedProduct.objects.aggregate(total=Sum('deposit'))['total'] or 0
        to_balance = PurchasedProduct.objects.aggregate(total=Sum('to_balance'))['total'] or 0
    elif is_client_user:
        recent_payments = Transaction.objects.filter(user=user).order_by('-created_at')[:5]
        purchased_property_ids = PurchasedProduct.objects.filter(user=user).values_list('id', flat=True)
        purchased_xCount = PurchasedProduct.objects.filter(user=user).count()
        properties = Property.objects.prefetch_related('images').filter(id__in=purchased_property_ids).order_by('-date_added')[:5]
        total_investment = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('deposit'))['total'] or 0
        to_balance = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('to_balance'))['total'] or 0
        total_price = PurchasedProduct.objects.filter(user=user).aggregate(total=Sum('price'))['total'] or 0
        if total_price and total_price > 0:
            payment_progress = round((total_investment / total_price) * 100, 2)

    full_payment_history_url = reverse('payment_history')
    property_count = properties.count()
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    # Chart Data
    labels = []
    data = []

    today = now()
    for i in range(5, -1, -1):
        target_date = today - timedelta(days=30 * i)
        month_label = target_date.strftime('%b %Y')
        labels.append(month_label)

        if is_admin_user:
            total = Transaction.objects.filter(
                created_at__year=target_date.year,
                created_at__month=target_date.month
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            total = Transaction.objects.filter(
                user=user,
                created_at__year=target_date.year,
                created_at__month=target_date.month
            ).aggregate(total=Sum('amount'))['total'] or 0

        data.append(round(total, 2))

    context = {
        'recent_payments': recent_payments,
        'full_payment_history_url': full_payment_history_url,
        'property': properties,
        'getDate': getDate,
        'purchased_xCount': purchased_xCount,
        'propertyCount': property_count,
        'user': user,
        'userFirstname': user.first_name,
        'is_client': is_client_user,
        'is_admin': is_admin_user,
        'total_investment': total_investment,
        'to_balance': to_balance,
        'payment_progress': payment_progress,
        'total_visitors': total_visitors,
        'transactions': transactions,
        'GoogleAPIKEY': settings.GOOGLE_MAPS_API_KEY,
        'chart_labels': labels,
        'chart_data': data,
    }

    return render(request, 'Dashboard/index.html', context)
