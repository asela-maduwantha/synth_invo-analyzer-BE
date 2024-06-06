import jwt
import datetime
import os
import random
from dotenv import load_dotenv
from rest_framework.exceptions import PermissionDenied
from .models import OTPVerification
import pyotp
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.utils import timezone

load_dotenv()

def generate_token(user_id, role):
    SECRET_KEY = os.getenv('SECRET_KEY')
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Adjust expiry time as needed
    created_time = datetime.datetime.utcnow()
    random_value = random.randint(1, 1000000)  
    payload = {'rand': random_value, 'user_id': user_id, 'role': role, 'exp': expiry_time, 'iat': created_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    SECRET_KEY = os.getenv('SECRET_KEY')
  

    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise PermissionDenied("Token has expired")
    except jwt.InvalidTokenError:
        raise PermissionDenied("Invalid token")


def send_email(clientMail, subject, message):
    try:
        with get_connection(
                host=settings.EMAIL_HOST, 
                port=settings.EMAIL_PORT,  
                username=settings.EMAIL_HOST_USER, 
                password=settings.EMAIL_HOST_PASSWORD, 
                use_tls=settings.EMAIL_USE_TLS
        ) as connection:
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [clientMail]
            EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()
            return True
    except Exception as e:
        print(e)
        return False

def send_otp(user_email):
    otp = pyotp.TOTP(pyotp.random_base32(), interval=60).now()  # OTP valid for 60 seconds
    try:
        OTPVerification.objects.create(user=user_email, otp=otp)
        subject = "Your Verification Code for SynthInvoAnalyzer"
        message = f"Your OTP is {otp}. Please enter this code in the appropriate field to complete the verification process. This OTP will expire in 1 minute, so please use it promptly. Thank you for choosing SynthInvoAnalyzer."
        send_status = send_email(user_email, subject, message)
        if send_status:
            return True
    except Exception as e:
        print(e)
        return False

def resend_otp(user_email):
    try:
        temp_user = OTPVerification.objects.get(user=user_email)
        temp_user.delete()
    except OTPVerification.DoesNotExist:
        pass
    return send_otp(user_email)

def verify_otp(user_email, user_otp):
    try:
        temp_user = OTPVerification.objects.get(user=user_email)
        if not temp_user.is_valid():
            return False, "OTP has expired"
        if temp_user.otp == user_otp:
            temp_user.verified = True
            temp_user.delete()
            return True, "Verified"
        else:
            return False, "Wrong OTP"
    except OTPVerification.DoesNotExist:
        return False, "No OTP found for this email"
    except Exception as e:
        print(e)
        return False, "Verification failed"
