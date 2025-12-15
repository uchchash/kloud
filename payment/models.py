from django.db import models
from django.conf import settings

STORAGE_UNIT_CHOICES = [
    ('GB', 'Gigabytes'), 
    ('TB', 'Terabytes')
    ]

STATUS_CHOICES = [
        ('active', 'Active'), 
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'), 
        ('trial', 'Trial'),
    ]
BILLING_CYCLE_CHOICES = [
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly')]
    

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    storage_amount = models.PositiveIntegerField()
    storage_unit = models.CharField(max_length=2, choices=STORAGE_UNIT_CHOICES, default="GB")
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    tier_order = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def storage_bytes(self):
        multiplier = 1024**3 if self.storage_unit == 'GB' else 1024**4
        return self.storage_amount * multiplier
    
    def __str__(self):
        return f"{self.name} - {self.storage_amount} {self.storage_unit}"


class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user} - {self.subscription_plan}"
    
    def is_active(self):
        return self.status == 'active'
    