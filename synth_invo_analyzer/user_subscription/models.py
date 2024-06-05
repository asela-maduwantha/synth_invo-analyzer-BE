from django.db import models
from authentication.models import Organization

class Subscription(models.Model):
    user = models.ForeignKey(Organization, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=100, unique=True)
    plan_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    billing_interval = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    payment_method = models.CharField(max_length=50)
    trial_period_days = models.IntegerField(default=0)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    auto_renewal = models.BooleanField(default=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

