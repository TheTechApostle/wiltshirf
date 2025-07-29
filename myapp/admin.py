from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(SliderImages)
admin.site.register(ClientRequest)
admin.site.register(ClientProfile)
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
# admin.site.register(SubscriptionPlan)
# admin.site.register(PropertySubscription)
admin.site.register(Transaction)
@admin.register(PurchasedProduct)
class PurchasedProductAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'property',
        'get_property_title',
        'method',
        'price',
        'deposit',
        'formatted_balance',
        'date_added',
    )
    list_filter = (
        'user',
        'property',
        'method',
        'date_added'
    )

    def get_property_title(self, obj):
        return obj.property.title if obj.property else obj.title
    get_property_title.short_description = 'Property Title'

    def formatted_balance(self, obj):
        return f"₦{obj.to_balance:,.2f}" if obj.to_balance else "₦0.00"
    formatted_balance.short_description = 'Remaining Balance'

admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Message)
admin.site.register(UploadedContract)

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


@admin.register(WithshirfReferral)
class WithshirfReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'referral_code', 'total_referrals', 'earnings', 'scheduled_payment_date','date_added')
    list_filter = ('user__username', 'referral_code', 'total_referrals','earnings')


class GalleryImageInline(admin.TabularInline):  # or admin.StackedInline
    model = GalleryImage
    extra = 1  # Number of empty forms to display
    fields = ('title', 'image', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)

@admin.register(GalleryImage)
class GalleryImageAmin(admin.ModelAdmin):
    list_display = ('event', 'title', 'image', 'uploaded_at')
    list_filter = ('event','title')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Preview'