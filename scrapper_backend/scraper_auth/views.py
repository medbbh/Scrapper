from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import random
import datetime
from .models import User, OTPVerification
from .serializers import (
    UserSerializer, LoginSerializer, OTPVerificationSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)

class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = str(random.randint(100000, 999999))
            OTPVerification.objects.create(user=user, otp=otp)
            
            # Send OTP via email
            send_mail(
                'Verify Your Account',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            return Response({
                "message": "Registration successful. Please verify your account with the OTP sent to your email."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            verification = OTPVerification.objects.filter(
                otp=otp,
                is_used=False,
                created_at__gte=datetime.datetime.now() - datetime.timedelta(minutes=10)
            ).first()
            
            if verification:
                user = verification.user
                user.is_phone_verified = True
                user.save()
                verification.is_used = True
                verification.save()
                
                return Response({
                    "message": "Account verified successfully."
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Invalid or expired OTP."
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                if not user.is_phone_verified:
                    return Response({
                        "message": "Please verify your account first."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Invalid credentials."
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            
            if user:
                token = str(RefreshToken.for_user(user))
                reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
                
                send_mail(
                    'Reset Your Password',
                    f'Click this link to reset your password: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                
                return Response({
                    "message": "Password reset link sent to your email."
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "User with this email does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = RefreshToken(serializer.validated_data['token'])
                user = User.objects.get(id=token['user_id'])
                user.set_password(serializer.validated_data['password'])
                user.save()
                
                return Response({
                    "message": "Password reset successful."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "message": "Invalid or expired token."
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
