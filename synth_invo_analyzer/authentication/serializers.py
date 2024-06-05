from rest_framework import serializers
from .models import User, Organization, SystemAdmin, Supplier, SupplierAddRequest, SupplierOrganization
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_verified_email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Organization
        fields = ['organization_id', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(is_organization=True, **user_data)  # Set is_organization to True
        organization = Organization.objects.create(user=user, **validated_data)
        return organization

class SystemAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SystemAdmin
        fields = ['admin_id', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(is_system_admin=True, **user_data)  # Set is_system_admin to True
        system_admin = SystemAdmin.objects.create(user=user, **validated_data)
        return system_admin

class SupplierSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Supplier
        fields = ['supplier_id', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(is_supplier=True, **user_data)  # Set is_supplier to True
        supplier = Supplier.objects.create(user=user, **validated_data)
        return supplier

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = ('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    

from rest_framework import serializers

class SupplierAddRequestSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='requested_by.user.username', read_only=True)
    
    class Meta:
        model = SupplierAddRequest
        fields = ['id', 'supplier_email', 'is_email_sent', 'is_accept', 'is_registered_supplier','requested_by' ,'organization_name', 'created_at']

        
class SupplierOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierOrganization
        fields = ['id', 'organization_id', 'supplier_id']