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


@admin.register(SubscriptionPropertyPlan)
class SubscriptionPropertyPlanAdmin(admin.ModelAdmin):
    list_display = ('property', 'duration_months', 'initial_deposit_percent', 'initial_payment', 'monthly_payment')
    list_filter = ('duration_months',)
    search_fields = ('property__title',)