from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage_display', 'monthly_price', 'yearly_price', 'tier_order', 'is_active')
    list_filter = ('is_active', 'storage_unit')
    ordering = ('tier_order',)
    
    def storage_display(self, obj):
        return f"{obj.storage_amount} {obj.storage_unit}"
    storage_display.short_description = 'Storage'
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_plan', 'status', 'billing_cycle', 'start_date', 'end_date')
    list_filter = ('status', 'billing_cycle', 'subscription_plan')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id')
    raw_id_fields = ('user',)