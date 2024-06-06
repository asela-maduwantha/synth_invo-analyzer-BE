from django.forms import ValidationError
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, OrganizationSerializer, SupplierAddRequestSerializer
from .models import Organization, SystemAdmin, Supplier, SupplierAddRequest, SupplierOrganization, User
from .utils import generate_token, decode_token, send_otp, resend_otp, verify_otp, send_email
from .permissions import IsOrganization, IsSupplier, IsSystemAdmin
import jwt
import datetime
import os
import random
from dotenv import load_dotenv
from rest_framework.exceptions import PermissionDenied
import pyotp
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.utils import timezone
load_dotenv()


@api_view(["POST"])
def organization_signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            organization = Organization.objects.create(user=user)
            send_otp(user.email)
            token = generate_token(organization.organization_id, 'organization')
            return Response({'token': token, 'user_id': organization.organization_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)  
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
        
@api_view(["POST"])
def system_admin_signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            system_admin = SystemAdmin.objects.create(user=user)
            send_otp(user.email)
            token = generate_token(system_admin.admin_id, 'system_admin')
            return Response({'token': token, 'user_id':system_admin.admin_id}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(["POST"])
def organization_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        try:
            organization = Organization.objects.get(user=user)
            if not user.is_verified_email:
                return Response({'error': 'Email should be verified', 'email': user.email}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            user.last_login = timezone.now()
            user.save()
            token = generate_token(organization.organization_id, 'organization')
            return Response({'token': token, 'user_id': organization.organization_id}, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response({'error': 'User is not associated with any organization.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid credentials or user is not an organization.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def system_admin_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        try:
            system_admin = SystemAdmin.objects.get(user=user)
            if not user.is_verified_email:
                return Response({'error': 'Email should be verified', 'email': user.email}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            token = generate_token(system_admin.admin_id, 'system_admin')
            return Response({'token': token, 'user_id': system_admin.admin_id}, status=status.HTTP_200_OK)
        except SystemAdmin.DoesNotExist:
            return Response({'error': 'User is not associated with any system admin.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid credentials or user is not a system admin.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def supplier_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        try:
            supplier = Supplier.objects.get(user=user)
            token = generate_token(supplier.supplier_id, 'supplier')
            return Response({'token': token, 'user_id': supplier.supplier_id}, status=status.HTTP_200_OK)
        except Supplier.DoesNotExist:
            return Response({'error': 'User is not associated with any supplier.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid credentials or user is not a supplier.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
# @permission_classes([IsOrganization])  
def add_supplier(request):
    try:
        supplier_email = request.data.get('supplier_email')
        organization_id = request.data.get('organization_id')

        if not supplier_email or not organization_id:
            return Response({'error': 'supplier_email and organization_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(organization_id=organization_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found.'}, status=status.HTTP_404_NOT_FOUND)

        if User.objects.filter(email=supplier_email).exists():
            supplier_user = User.objects.get(email=supplier_email)
            if Supplier.objects.filter(user=supplier_user).exists():
                supplier = Supplier.objects.get(user=supplier_user)
                if SupplierOrganization.objects.filter(organization=organization, supplier=supplier).exists():
                    return Response({'error': 'This supplier is already added to the organization.'}, status=status.HTTP_400_BAD_REQUEST)
                
                
                email_body = f'Hello,\n\nIf you are a supplier of {organization.user.username}, please confirm that through this link: http://localhost:3000/supplier/register.'
                send_email(supplier_email, 'Supplier Confirmation', email_body)
                new_request = SupplierAddRequest.objects.create(
                                supplier_email=supplier_email,
                                requested_by=organization,
                                is_email_sent = True,
                                is_registered_supplier = True,
                                )
                new_request.save()
            else:
                email_body = f'Hello,\n\nThis organization would like to add you as a supplier. Join us by completing a few registration steps through this link: http://localhost:3000.'
                send_email(supplier_email, 'Supplier Confirmation', email_body)
                new_request = SupplierAddRequest.objects.create(
                                supplier_email=supplier_email,
                                requested_by=organization,
                                is_email_sent = True,
                                is_registered_supplier = False,
                                )
                new_request.save()
        else:
            email_body = f'Hello,\n\nThis organization would like to add you as a supplier. Join us by completing a few registration steps through this link: http://localhost:3000.'
            send_email(supplier_email, 'Supplier Confirmation', email_body)
            new_request = SupplierAddRequest.objects.create(
                                supplier_email=supplier_email,
                                requested_by=organization,
                                is_email_sent = True,
                                is_registered_supplier = False,
                                )
            new_request.save()

        

        

        return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': 'Internal Server Error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
@api_view(["POST"])
def supplier_register(request):
    try:
        supplier_email = request.data.get('email')

        add_request = SupplierAddRequest.objects.filter(supplier_email=supplier_email).first()
        if not add_request:
            return Response({'error': 'Supplier email not found in the add request table.'}, status=status.HTTP_400_BAD_REQUEST)

        add_request.is_accept = True
        add_request.save()

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            supplier = Supplier.objects.create(user=user)
            
            supplier_organization = SupplierOrganization.objects.create(
                organization_id = add_request.requested_by_id,
                supplier_id = supplier.supplier_id
            )
            supplier_organization.save()
            token = generate_token(supplier.supplier_id, 'supplier')
            return Response({'token': token, 'user_id':supplier.supplier_id}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(['GET'])
def organizations_by_supplier(request, supplier_id):
    supplier = Supplier.objects.filter(supplier_id=supplier_id).first()

    if supplier is None:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve organizations associated with the given supplier
    organizations = Organization.objects.filter(supplierorganization__supplier_id=supplier)

    # Serialize the organizations to retrieve organization_id and username
    serializer = OrganizationSerializer(organizations, many=True)
    serialized_data = [{'organization_id': org.organization_id, 'username': org.user.username} for org in organizations]

    return Response({'organizations': serialized_data}, status=status.HTTP_200_OK)



@api_view(["POST"])
def send_otp_view(request):
    user_email = request.data.get("email")
    
    if not user_email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=user_email)
        if user.is_verified_email:
            return Response({"error": "User's email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        if send_otp(user_email):
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def verify_otp_view(request):
    user_email = request.data.get("email")
    user_otp = request.data.get("otp")
    
    if not user_email or not user_otp:
        return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=user_email)
        if user.is_verified_email:
            return Response({"error": "User's email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        is_verified, message = verify_otp(user_email, user_otp)
        if is_verified:
            user.is_verified_email = True
            user.save()
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def resend_otp_view(request):
    user_email = request.data.get("email")
    
    if not user_email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=user_email)
        if user.is_verified_email:
            return Response({"error": "User's email is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        if resend_otp(user_email):
            return Response({"message": "OTP resent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to resend OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET'])
def add_requests_by_supplier_id(request, supplier_id):
    try:
        supplier = Supplier.objects.get(supplier_id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        supplier_user = User.objects.get(id=supplier.user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    add_requests = SupplierAddRequest.objects.filter(supplier_email=supplier_user.email, is_registered_supplier=True)
    
    if not add_requests.exists():
        return Response({'error': 'No add requests found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SupplierAddRequestSerializer(add_requests, many=True)
    
    # Format the response data to include requested organization and requested time
    response_data = []
    for data in serializer.data:
        response_data.append({
            'requested_organization': data['organization_name'],
            'request_id' : data['id'],
            'requested_time': data['created_at'],
        })
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def accept_request(request, request_id):
    supplier_id = request.data.get('user_id')
    if not supplier_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        supplier = Supplier.objects.get(supplier_id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        add_request = SupplierAddRequest.objects.get(id=request_id)
        add_request.is_accept = True
        
        supplier_organization = SupplierOrganization.objects.create(
            organization=add_request.requested_by,
            supplier=supplier
        )
        supplier_organization.save()
        add_request.delete()
        return Response({'success': 'Request accepted'}, status=status.HTTP_200_OK)
    except SupplierAddRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def dismiss_request(request, request_id):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        add_request = SupplierAddRequest.objects.get(id=request_id)
        add_request.delete()
        return Response({'success': 'Request dismissed'}, status=status.HTTP_200_OK)
    except SupplierAddRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsOrganization])
def OrganizationProtectedView(request):
    return Response({'message': 'Authenticated'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsSystemAdmin])
def AdminProtectedView(request):
    return Response({'message': 'Authenticated'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsSupplier])
def SupplierProtectedView(request):
    return Response({'message': 'Authenticated'}, status=status.HTTP_200_OK)

