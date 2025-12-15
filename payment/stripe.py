import stripe
from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")