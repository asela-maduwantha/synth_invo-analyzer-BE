from django.db import models
from authentication.models import SystemAdmin

class SubscriptionModel(models.Model):
    model_id = models.AutoField(primary_key=True)
    stripe_id = models.TextField()
    price_id = models.TextField()
    model_name = models.CharField(max_length=10)
    model_price = models.IntegerField()
    billing_period = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(SystemAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_subscriptions')
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(SystemAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_subscriptions')


class SubscriptionModelFeatures(models.Model):
    feature = models.CharField(max_length=50)
    model = models.ForeignKey(SubscriptionModel, on_delete=models.CASCADE, related_name='models')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(SystemAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscription_features')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(SystemAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_subscription_features')
    
    class Meta:
        unique_together = ('feature', 'model')
