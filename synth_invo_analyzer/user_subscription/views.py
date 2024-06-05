from django.shortcuts import redirect
from django.http import HttpResponse
from rest_framework.decorators import api_view
import stripe
import os
from dotenv import load_dotenv
from .models import Subscription, Payment
from datetime import datetime

load_dotenv()

@api_view(['POST'])
def createSubscription(request):
    price_id = request.data['priceId']
    print(price_id)
    
    stripe.api_key = os.getenv("STRIPE_KEY")

    try:
        session = stripe.checkout.Session.create(
            success_url='http://localhost:3000/organization?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/pricing',
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1
            }],
        )

        return HttpResponse(session.url, status=200)
    except Exception as e:
        print(e)
        return HttpResponse(str(e), status=500)
    


@api_view(['POST'])
def stripe_webhook(request):
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_KEY")
    stripe.api_key = os.getenv("STRIPE_KEY")

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print("ValueError:", e)
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError as e:
        print("SignatureVerificationError:", e)
        return HttpResponse("Invalid signature", status=400)

    event_type = event['type']
    print(event_type)
    try:
        if event_type == 'customer.subscription.created':
            handle_subscription_created(event)
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(event)
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(event)
    except Exception as e:
        print(f"Error handling event {event_type}: {e}")
        return HttpResponse(f"Error handling event {event_type}", status=500)

    return HttpResponse(status=200)

def handle_subscription_created(event_json):
    try:
        subscription_data = event_json['data']['object']
        subscription_id = subscription_data['id']
        user_id = subscription_data['customer']
        plan_id = subscription_data['plan']['id']
        status = subscription_data['status']

        start_date = subscription_data['start_date']
        if isinstance(start_date, int):
            start_date = datetime.fromtimestamp(start_date).isoformat()

        next_billing_date = subscription_data.get('current_period_end')
        if next_billing_date and isinstance(next_billing_date, int):
            next_billing_date = datetime.fromtimestamp(next_billing_date).isoformat()

        billing_interval = subscription_data['plan']['interval']
        amount = subscription_data['plan']['amount']
        currency = subscription_data['plan']['currency']
        payment_method = subscription_data['default_payment_method']
        trial_period_days = subscription_data.get('trial_period_days', 0)

        subscription_obj = Subscription.objects.create(
            subscription_id=subscription_id,
            user_id=6,
            plan_id=plan_id,
            status=status,
            start_date=start_date,
            billing_interval=billing_interval,
            amount=amount,
            currency=currency,
            payment_method='card',
            trial_period_days=trial_period_days,
            next_billing_date=next_billing_date,
        )
        subscription_obj.save()
        print(f"Subscription created: {subscription_obj}")
    except Exception as e:
        print(f"Error saving subscription: {e}")
        raise

def handle_payment_succeeded(event_json):
    try:
        payment_data = event_json['data']['object']
        subscription_id = payment_data['subscription']
        payment_id = payment_data['id']
        payment_date = payment_data['created']
        status = payment_data['status']
        amount_paid = payment_data['amount_paid']
        invoice_id = payment_data.get('invoice', "N/A")

        # Retrieve the Subscription object
        subscription_obj = Subscription.objects.get(subscription_id=subscription_id)

        payment_obj = Payment.objects.create(
            subscription=subscription_obj,
            payment_id=payment_id,
            payment_date=datetime.fromtimestamp(payment_date).isoformat(),
            status=status,
            amount_paid=amount_paid,
            invoice_id=invoice_id,
        )
        payment_obj.save()
        print(f"Payment succeeded: {payment_obj}")
    except Subscription.DoesNotExist:
        print(f"Subscription with id {subscription_id} does not exist")
    except Exception as e:
        print(f"Error saving payment: {e}")
        raise

def handle_payment_failed(event_json):
    try:
        payment_data = event_json['data']['object']
        subscription_id = payment_data['subscription']
        payment_id = payment_data['id']
        payment_date = payment_data['created']
        status = payment_data['status']
        amount_paid = payment_data.get('amount_paid', 0)
        invoice_id = payment_data.get('invoice', "N/A")

        # Retrieve the Subscription object
        subscription_obj = Subscription.objects.get(subscription_id=subscription_id)

        payment_obj = Payment.objects.create(
            subscription=subscription_obj,
            payment_id=payment_id,
            payment_date=datetime.fromtimestamp(payment_date).isoformat(),
            status=status,
            amount_paid=amount_paid,
            invoice_id=invoice_id,
        )
        payment_obj.save()
        print(f"Payment failed: {payment_obj}")
    except Subscription.DoesNotExist:
        print(f"Subscription with id {subscription_id} does not exist")
    except Exception as e:
        print(f"Error saving payment failed record: {e}")
        raise

