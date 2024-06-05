from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

class User(AbstractUser):
    is_verified_email = models.BooleanField(default=False)
    
class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class SystemAdmin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
    

# class CustomAccessToken(AccessToken):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
       
#         self['role'] = 'organization'  

class OTPVerification(models.Model):
    user = models.EmailField(primary_key=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def is_valid(self):
        current_time = timezone.now()  
        time_difference = (current_time - self.created_at).seconds
        return time_difference < 60  


class SupplierAddRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    supplier_email = models.EmailField(unique=True)
    is_email_sent = models.BooleanField(default = False)
    is_accept = models.BooleanField(default = False)
    is_registered_supplier = models.BooleanField(default = False)
    requested_by = models.OneToOneField(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class SupplierOrganization(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('organization', 'supplier')

