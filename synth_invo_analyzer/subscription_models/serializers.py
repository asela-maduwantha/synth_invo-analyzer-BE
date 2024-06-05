from .models import SubscriptionModel, SubscriptionModelFeatures
from rest_framework import serializers
from authentication.serializers import SystemAdminSerializer

class SubscriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ['model_id', 'stripe_id', 'price_id', 'model_name', 'model_price', 'billing_period', 'created_by', 'last_modified_by']


class SubscriptionModelFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModelFeatures
        fields = ['id', 'feature', 'model', 'created_at', 'created_by', 'modified_at', 'modified_by']
        read_only_fields = ['created_at', 'modified_at']