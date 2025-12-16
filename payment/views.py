from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from payment.models import SubscriptionPlan, UserSubscription
from payment.stripe import stripe
from dotenv import load_dotenv
from vault.models import Member
import os
from datetime import datetime, timedelta

load_dotenv()

User = get_user_model()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@csrf_exempt
@login_required
def create_checkout_session(request):
    plan_id = request.POST.get("plan_id") # Get plan_id from POST data 
    billing_cycle = request.POST.get("billing_cycle") # Billing cycle for accurate amount
    plan = get_object_or_404(SubscriptionPlan, id=plan_id) #Plan data

    if billing_cycle == "monthly":
        price_id = plan.stripe_price_id_monthly # Monthly price ID
    elif billing_cycle == "yearly":
        price_id = plan.stripe_price_id_yearly # Yearly price ID
    else:
        return JsonResponse({"error": "Invalid billing cycle"}, status=400)

    customer_email = request.user.email # User email for Stripe customer
    user_id = request.user.id # User ID for metadata

    checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="http://localhost:8000/vault/dashboard/", #If checkout is successful
        cancel_url="http://localhost:8000/", #If checkout is cancelled
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
    payload = request.body # Raw payload from Stripe
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE') # Signature header
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET") # Webhook secret

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret) # Verify event
    except ValueError:
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature:", e)
        return HttpResponse(status=400)

    event_type = event['type'] # Event type
    data = event['data']['object'] # Event data object
    print(f"Received webhook: {event_type}")
    print(f"DEBUG: Event Payload: {data}")

    if event_type == 'checkout.session.completed': # Checkout completed
        user_id = data['metadata'].get('user_id') # Get user ID from metadata
        plan_id = data['metadata'].get('plan_id') # Get plan ID from metadata
        billing_cycle = data['metadata'].get('billing_cycle') # Get billing cycle from metadata

        if user_id:
            user = User.objects.get(id=user_id) # Fetch user from DB
            UserSubscription.objects.filter(user=user, status='active').update(status='cancelled') # Cancel existing subscriptions

            if billing_cycle == 'monthly':
                end_date = datetime.now() + timedelta(days=30) # Set end date for monthly
            elif billing_cycle == 'yearly':
                end_date = datetime.now() + timedelta(days=365) # Set end date for yearly
            else:
                end_date = None # Fallback

            subscription = UserSubscription.objects.create(
                user=user,
                subscription_plan_id=plan_id,
                billing_cycle=billing_cycle,
                stripe_subscription_id=data.get("subscription"),
                stripe_customer_id=data.get("customer"),
                status='active',
                end_date=end_date
            )

            try:
                if not hasattr(user, 'member'): # Ensure Member profile exists
                     Member.objects.create(user=user) # Create Member profile if missing
                user.member.current_plan = subscription # Update Member profile
                user.member.save() # Save changes
                print(f"DEBUG: Member plan updated for {user.email}")
            except Exception as e:
                print(f"ERROR: Failed to update member plan: {e}")
            print(f"Subscription activated for {user.email} until {end_date}")

    elif event_type == 'customer.subscription.deleted': # Subscription cancelled
        subscription_id = data['id'] # Get subscription ID
        UserSubscription.objects.filter(stripe_subscription_id=subscription_id).update(status='cancelled') # Update status to cancelled
        print(f"Subscription {subscription_id} cancelled")
    elif event_type == 'invoice.payment_succeeded': # Payment succeeded
        subscription_id = data.get('subscription') # Get subscription ID
        subscription = UserSubscription.objects.filter(stripe_subscription_id=subscription_id, status='active').first()
        if subscription:
            period_end = None 
            try:
                lines = data['lines']
                if lines and lines['data']:
                    period_end = lines['data'][0]['period']['end']
            except (KeyError, TypeError, IndexError):
                pass

            if period_end: # If period end is available from Stripe
                 subscription.end_date = datetime.fromtimestamp(period_end) # Update end date from Stripe data
            else:
                if subscription.billing_cycle == 'monthly':
                    subscription.end_date = datetime.now() + timedelta(days=30) # Set end date for monthly
                elif subscription.billing_cycle == 'yearly':
                    subscription.end_date = datetime.now() + timedelta(days=365) # Set end date for yearly
            
            subscription.save() # Save changes
            print(f"Subscription {subscription_id} renewed/verified, new end date: {subscription.end_date}")

    elif event_type == 'invoice.payment_failed': # Payment failed
        subscription_id = data.get('subscription') # Get subscription ID
        subscription = UserSubscription.objects.filter(stripe_subscription_id=subscription_id, status='active').first() # Fetch active subscription
        if subscription:
            subscription.status = 'cancelled' # Update status to cancelled
            subscription.save() # Save changes
            print(f"Subscription {subscription_id} payment failed → cancelled")

    return HttpResponse(status=200)

