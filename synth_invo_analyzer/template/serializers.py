from rest_framework import serializers
from .models import InternalInvoiceFormat, InvoiceTemplate
import uuid
from datetime import datetime


class InternalInvoiceFormatSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(default=uuid.uuid4)  
    uploaded_user = serializers.IntegerField()  
    internal_format = serializers.CharField()  
    uploaded_at = serializers.DateTimeField(default=datetime.now)  
    attributes = serializers.ListField(
        child=serializers.CharField(),  
        allow_empty=True  
    )

    class Meta:
        model = InternalInvoiceFormat  # Link to the corresponding model
        fields = ['id', 'uploaded_user', 'internal_format', 'uploaded_at', 'attributes']  \
            
class InvoiceTemplateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(default=uuid.uuid4)
    supplier = serializers.IntegerField()
    template_name = serializers.CharField()
    template_content = serializers.CharField()
    attributes = serializers.ListField(child=serializers.CharField())
    uploaded_at = serializers.DateTimeField()

    class Meta:
        model = InvoiceTemplate
        fields = ['id', 'supplier', 'template_name', 'template_content', 'attributes', 'uploaded_at']