from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_HALF_UP
from .signals import *

# Create your models here.
class SliderImages(models.Model):
    sliderText = models.TextField("Slider Text", max_length=200)
    sliderImage = models.FileField(upload_to="slider_images/")


    def __str__(self):
        return self.sliderText[:50]

# Property type model
class PropertyType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Location model
class Location(models.Model):
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"


# Property model
class Property(models.Model):
    featureChoice = [
        ('For Sell', 'For Sell'),
        ('For Rent', 'For Rent'),
        ('Sub-Let', 'Sub-Let')
    ]
    PropertyStatus = [
        ('Still Selling', 'Still Selling'),
        ('Taken', 'Taken'),
        ('Leased Out', 'Leased Out')
    ]
    AllowedSubscription = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    property_status = models.TextField("Property Status", choices=PropertyStatus, max_length=50)
    propertyFeature = models.CharField("feature Choice", choices=featureChoice, max_length=50)
    allSubscription = models.CharField(choices=AllowedSubscription, max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.property_type.name}"
    
class PropertyImage(models.Model):
    VIEW_CHOICES = [
        ('front', 'Front View'),
        ('back', 'Back View'),
        ('side', 'Side View'),
        ('palour', 'Palour View'),
        ('kitchen', 'Kitchen View'),
        ('bedroom', 'Bedroom View'),
        # add more as needed
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    label = models.CharField(max_length=50, choices=VIEW_CHOICES)

    def __str__(self):
        return f"{self.label.title()} - {self.property.title}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)  # e.g., "3-Month Plan"
    duration_months = models.PositiveIntegerField()  # e.g., 3
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.duration_months} months)"
    


class PropertySubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    

    is_active = models.BooleanField(default=True)
    started_at = models.DateField(auto_now_add=True)
    next_payment_date = models.DateField()

    def __str__(self):
        return f"{self.property} - {self.plan}"


   

# What the client wants (Client Request)
class ClientRequest(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    preferred_property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    preferred_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(help_text="What kind of property do you want?", null=True, blank=True)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.preferred_property_type.name}"

# models.py



class Agent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='agent_profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ClientTestimony(models.Model):
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    statement = models.CharField(max_length=200)
    profile_picture = models.ImageField(upload_to='client_profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')




class SubscriptionPropertyPlan(models.Model):
    property = models.ForeignKey("Property", on_delete=models.CASCADE, related_name='subscription_plans')
    duration_months = models.PositiveIntegerField(help_text="Enter duration in months (e.g. 4, 5, 9)")
    initial_deposit_percent = models.PositiveIntegerField(default=30, help_text="e.g. 30 for 30% deposit")
    
    initial_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    auto_balance = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.property.title} – {self.duration_months} Month Plan"
    
    def save(self, *args, **kwargs):
        if self.property.allSubscription != 'Yes':
            raise ValueError("This property does not support subscription plans.")

        if not (1 <= self.initial_deposit_percent < 100):
            raise ValueError("Initial deposit percent must be between 1 and 99.")

        if self.duration_months < 1:
            raise ValueError("Duration must be at least 1 month.")

        total_price = Decimal(self.property.price)
        deposit_percent = Decimal(self.initial_deposit_percent)

        # Exact calculation without rounding
        self.initial_payment = total_price * (deposit_percent / Decimal(100))

        if self.duration_months > 1:
            remaining_amount = total_price - self.initial_payment
            months_remaining = self.duration_months
            self.monthly_payment = remaining_amount / Decimal(months_remaining)
        else:
            self.monthly_payment = Decimal("0.00")

        super().save(*args, **kwargs)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reference}"

class PurchasedProduct(models.Model):
    paymentMethod = [
        ('Wallet', 'Wallet'),
        ('Paystack', 'Paystack')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    method= models.CharField(choices=paymentMethod, max_length=50)
    price = models.FloatField()
    deposit = models.FloatField(null=True, blank=True)
    to_balance = models.FloatField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username
    


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet: ₦{self.balance}"
    

class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"₦{self.amount} - {self.reference}"


# models.py

class PaymentTransactionTrash(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add soft delete flag
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - ₦{self.amount}"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']