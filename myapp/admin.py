from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(SliderImages)
admin.site.register(ClientRequest)
class PropertyImageInline(admin.TabularInline):  # or admin.StackedInline
    model = PropertyImage
    extra = 1

class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'property_type', 'location', 'date_added']
    inlines = [PropertyImageInline]

admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)  
admin.site.register(PropertyType)  
admin.site.register(Location)
admin.site.register(Agent)
admin.site.register(ClientTestimony)
admin.site.register(Cart)
admin.site.register(SubscriptionPlan)
admin.site.register(PropertySubscription)
admin.site.register(Transaction)
admin.site.register(PurchasedProduct)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Message)

@admin.register(SubscriptionPropertyPlan)
class SubscriptionPropertyPlanAdmin(admin.ModelAdmin):
    list_display = ('property', 'duration_months', 'initial_deposit_percent', 'initial_payment', 'monthly_payment','increase_every_n_months','increase_percentage','total_amount_payable')
    list_filter = ('duration_months',)
    search_fields = ('property__title',)

@admin.register(PaymentTransactionTrash)
class PaymentTransactionTrashAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reference', 'status', 'created_at', 'is_trashed')
    list_filter = ('user', 'status', 'is_trashed', 'created_at')


@admin.register(PurchasedProductTrash)
class PurchasedProductTrashAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'price', 'transaction_reference', 'date_removed')
    list_filter = ('user', 'method', 'date_removed')

