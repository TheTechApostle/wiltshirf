from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import PurchasedProduct, SubscriptionPropertyPlan

@shared_task
def update_balances():
    now = timezone.now().date()
    products = PurchasedProduct.objects.filter(property__isnull=False)

    for product in products:
        plan = SubscriptionPropertyPlan.objects.filter(property=product.property).first()
        if not plan or not plan.increase_every_n_months or not plan.increase_percentage:
            continue

        months_elapsed = (now.year - product.date_added.year) * 12 + (now.month - product.date_added.month)
        increments_due = months_elapsed // plan.increase_every_n_months

        if increments_due > 0:
            original_balance = product.to_balance or 0
            new_balance = Decimal(original_balance)

            for _ in range(increments_due):
                new_balance += (plan.increase_percentage / Decimal(100)) * new_balance

            product.to_balance = float(round(new_balance, 2))
            product.save()
            updated_count += 1

    return f"{updated_count} products updated"
