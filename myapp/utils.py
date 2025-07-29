import requests
from django.conf import settings

def is_admin(user):     
    return user.groups.filter(name='admin').exists()

def is_client(user):
    return user.groups.filter(name='client').exists()


def is_referrer(user):
    return user.groups.filter(name='referrer').exists()

from decimal import Decimal, InvalidOperation

def safe_decimal(value):
    try:
        return Decimal(str(value).replace(',', '').strip())
    except (InvalidOperation, ValueError, TypeError):
        return None
        




def get_all_bank_codes():
    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("status"):
        banks = data.get("data", [])
        # Lowercase bank names for easier matching
        bank_map = {bank["name"].lower(): bank["code"] for bank in banks}
        return bank_map
    else:
        raise Exception("Failed to fetch banks from Paystack")



def create_transfer_recipient(account_name, account_number, bank_code):
    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "type": "nuban",
        "name": account_name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "NGN"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

def initiate_transfer(amount, reason, recipient_code):
    url = "https://api.paystack.co/transfer"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "source": "balance",
        "amount": int(float(amount) * 100),  # Paystack expects amount in kobo
        "recipient": recipient_code,
        "reason": reason
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()
