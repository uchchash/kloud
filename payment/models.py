from django.db import models

STORAGE_UNIT_CHOICES = [
    ('GB', 'Gigabytes'), 
    ('TB', 'Terabytes')
    ]

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    storage_amount = models.PositiveIntegerField()
    storage_unit = models.CharField(max_length=2, choices=STORAGE_UNIT_CHOICES, default="GB")
    monthly_price = models.DecimalField(max_length=10, decimal_places=2)
    yearly_price = models.DecimalField(max_length=10, decimal_places=2)
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True)
    stripe_price_id_yearly = models.CharField(max_length=100, blank=True)
    tier_order = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def storage_bytes(self):
        multiplier = 1024**3 if self.storage_unit == 'GB' else 1024**4
        return self.storage_amount * multiplier



