from rest_framework import serializers
from .models import Invoice
import uuid
from datetime import datetime

class InvoiceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(default=uuid.uuid4)
    issuer = serializers.IntegerField()
    recipient = serializers.IntegerField()
    source_format = serializers.CharField()  
    internal_format = serializers.CharField()  
    created_at = serializers.DateTimeField(default=datetime.now)

    class Meta:
        model = Invoice
        fields = ['id', 'issuer', 'recipient', 'source_format', 'internal_format', 'created_at']
