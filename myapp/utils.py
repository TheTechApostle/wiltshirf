def is_admin(user):     
    return user.groups.filter(name='admin').exists()

def is_client(user):
    return user.groups.filter(name='client').exists()


from decimal import Decimal, InvalidOperation

def safe_decimal(value):
    try:
        return Decimal(str(value).replace(',', '').strip())
    except (InvalidOperation, ValueError, TypeError):
        return None