from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import Organization, Supplier, SystemAdmin
from .utils import decode_token

class IsOrganization(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.headers.get('Authorization')

        if not token:
            raise PermissionDenied("Token is missing")
 
        user_info = decode_token(token)

        if 'user_id' not in user_info or 'role' not in user_info:
            raise PermissionDenied("Invalid token")

        user_id = user_info['user_id']
        role = user_info['role']
        if role == 'organization':
            if Organization.objects.filter(organization_id=user_id).exists():
                return True
      
        raise PermissionDenied("You do not have permission to access this resource as an organization")


class IsSupplier(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.headers.get('Authorization')

        if not token:
            raise PermissionDenied("Token is missing")

        user_info = decode_token(token)

        if 'user_id' not in user_info or 'role' not in user_info:
            raise PermissionDenied("Invalid token")

        user_id = user_info['user_id']
        role = user_info['role']

        if role == 'supplier':
            if Supplier.objects.filter(supplier_id=user_id).exists():
                return True

        raise PermissionDenied("You do not have permission to access this resource as a supplier")


class IsSystemAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        token = request.headers.get('Authorization')
        
        if not token:
            raise PermissionDenied("Token is missing")

        user_info = decode_token(token)

        if 'user_id' not in user_info or 'role' not in user_info:
            raise PermissionDenied("Invalid token")

        user_id = user_info['user_id']
        role = user_info['role']

        if role == 'system_admin':
            if SystemAdmin.objects.filter(admin_id=user_id).exists():
                return True

        raise PermissionDenied("You do not have permission to access this resource as a system admin")
