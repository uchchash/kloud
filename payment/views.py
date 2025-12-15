from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from payment.models import SubscriptionPlan, UserSubscription
from payment.stripe import stripe
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@csrf_exempt
def create_checkout_session(request):
    plan_id = request.POST.get("plan_id")
    billing_cycle = request.POST.get("billing_cycle") 
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if billing_cycle == "monthly":
        price_id = plan.stripe_price_id_monthly
    elif billing_cycle == "yearly":
        price_id = plan.stripe_price_id_yearly
    else:
        return JsonResponse({"error": "Invalid billing cycle"}, status=400)

    customer_email = request.user.email if request.user.is_authenticated else "test@example.com"
    user_id = request.user.id if request.user.is_authenticated else 1  # for testing

    checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="http://localhost:8000/dashboard/",
        cancel_url="http://localhost:8000/",
        customer_email=customer_email,
        metadata={
            "user_id": user_id,
            "plan_id": plan.id,
            "billing_cycle": billing_cycle,
        }
    )

    return JsonResponse({"checkout_url": checkout_session.url})



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature:", e)
        return HttpResponse(status=400)

    event_type = event['type']
    data = event['data']['object']
    print("Received webhook:", event_type)

    if event_type == 'checkout.session.completed':
        user_id = data['metadata'].get('user_id')
        plan_id = data['metadata'].get('plan_id')
        billing_cycle = data['metadata'].get('billing_cycle')

        if user_id:
            user = User.objects.get(id=user_id)
            UserSubscription.objects.filter(user=user, status='active').update(status='canceled')

            if billing_cycle == 'monthly':
                end_date = datetime.now() + timedelta(days=30)
            elif billing_cycle == 'yearly':
                end_date = datetime.now() + timedelta(days=365)
            else:
                end_date = None

            UserSubscription.objects.create(
                user=user,
                subscription_plan_id=plan_id,
                billing_cycle=billing_cycle,
                stripe_subscription_id=data.get("subscription"),
                stripe_customer_id=data.get("customer"),
                status='active',
                end_date=end_date
            )
            print(f"Subscription activated for {user.email} until {end_date}")

    elif event_type == 'customer.subscription.deleted':
        subscription_id = data['id']
        UserSubscription.objects.filter(stripe_subscription_id=subscription_id).update(status='canceled')
        print(f"Subscription {subscription_id} canceled")
    elif event_type == 'invoice.payment_succeeded':
        subscription_id = data.get('subscription')
        subscription = UserSubscription.objects.filter(stripe_subscription_id=subscription_id, status='active').first()
        if subscription:
            if subscription.billing_cycle == 'monthly':
                subscription.end_date += timedelta(days=30)
            elif subscription.billing_cycle == 'yearly':
                subscription.end_date += timedelta(days=365)
            subscription.save()
            print(f"Subscription {subscription_id} renewed, new end date: {subscription.end_date}")

    elif event_type == 'invoice.payment_failed':
        subscription_id = data.get('subscription')
        subscription = UserSubscription.objects.filter(stripe_subscription_id=subscription_id, status='active').first()
        if subscription:
            subscription.status = 'canceled'
            subscription.save()
            print(f"Subscription {subscription_id} payment failed → canceled")

    return HttpResponse(status=200)