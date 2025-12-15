from django.core.management.base import BaseCommand
from payment.stripe import stripe
from payment.models import SubscriptionPlan, UserSubscription


class Command(BaseCommand):
    help = "Sync subscription plans with Stripe"

    def handle(self, *args, **options):
        for plan in SubscriptionPlan.objects.all():
            if not plan.stripe_product_id:
                product = stripe.Product.create(
                    name=plan.name,
                    metadata={"plan_id": plan.id}
                )
                plan.stripe_product_id = product.id
                plan.save()
            
            if not plan.stripe_price_id_monthly:
                price = stripe.Price.create(
                    product=plan.stripe_product_id,
                    unit_amount=int(plan.monthly_price * 100),
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={
                        "plan_id": plan.id,
                        "billing": "monthly"
                    }
                )
                plan.stripe_price_id_monthly = price.id
                plan.save()

            if not plan.stripe_price_id_yearly:
                price = stripe.Price.create(
                    product=plan.stripe_product_id,
                    unit_amount=int(plan.yearly_price * 100),
                    currency="usd",
                    recurring={"interval": "year"},
                    metadata={
                        "plan_id": plan.id,
                        "billing": "yearly"
                    }
                )
                plan.stripe_price_id_yearly = price.id
                plan.save()

        self.stdout.write(self.style.SUCCESS("Stripe plans synced"))

class Command(BaseCommand):
    help = "Deactivate expired subscriptions"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_subs = UserSubscription.objects.filter(status='active', end_date__lt=now)
        expired_subs.update(status='cancelled')
        self.stdout.write(f"Deactivated {expired_subs.count()} expired subscriptions")