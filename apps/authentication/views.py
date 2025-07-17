from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.core.models import User
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from security.password import check_password_security
# from apps.common.services.email_service import send_email
from datetime import datetime, timezone
from django.conf import settings

import jwt

class ForgotPasswordView(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_description="Request password recovery by email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email address'),
            },
        ),
        responses={
            200: openapi.Response(
                description="Recovery code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid email",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            print(user)
            refresh = RefreshToken.for_user(user)
            token = refresh.access_token
            user.recovery_code = str(token)
            user.save()
            # send_email(
            #     template_name='forgot_password.html',
            #     context={
            #         'reset_link': f"{settings.FRONT_URL}/reset-password?code={str(token)}"
            #     },
            #     to=user.email,
            #     subject='Recupera tu contraseña - BuenCapital'
            # )
            return Response({'message': 'Recovery code sent to your email'}, status=200)
        
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)

class ResetPasswordView(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_description="Reset password using recovery code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password'],
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
                'recovery_code': openapi.Schema(type=openapi.TYPE_STRING, description='Recovery code'),
            },
        ),
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid recovery code or password requirements not met",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'errors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='List of error messages'
                        )
                    }
                )
            )
        }
    )
    @check_password_security
    def put(self, request, *args, **kwargs):
        recovery_code = request.data.get('recovery_code')
        password = request.data.get('password')
        try:
            user = User.objects.get(recovery_code=recovery_code)
        except User.DoesNotExist:
            return Response({'error': 'Invalid recovery code'}, status=400)
        decoded_token = jwt.decode(recovery_code, settings.SECRET_KEY, algorithms=["HS256"])

        exp_timestamp = decoded_token.get('exp')
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        if datetime.now(timezone.utc) > exp_datetime:
            return Response({"error": "Token expired"}, status=403)
        user.set_password(password)
        user.recovery_code = None
        user.save()

        return Response({'message': 'Password changed successfully'}, status=200)

class RegisterUserView(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'first_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),  
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User first name'),
            }
        ))
    @check_password_security
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        try:
            user = User.objects.get(email=email)
            return Response({'error': 'Email already exists'}, status=400)
        except User.DoesNotExist:
            user = User.objects.create_user(email=email, password=password, name=name, username=email, is_active= False)
            return Response({'message': 'User created successfully'}, status=201)

class LoginUserView(APIView):
    permission_classes = []
    @swagger_auto_schema(
        operation_description="Login user and return an access token if credentials are valid.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged in. Returns an access token.",
                examples={
                    "application/json": {"access": "your_access_token_here", "email": "user@mail.com", "role": "admin"}
                }
            ),
            400: openapi.Response(
                description="Invalid credentials provided.",
                examples={
                    "application/json": {"error": "Invalid credentials"}
                }
            ),
            403: openapi.Response(
                description="User is inactive. Contact support.",
                examples={
                    "application/json": {"error": "User inactive, contact support"}
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=400)
        
        try:
            user = User.objects.get(email=email)

            if not user.is_active:
                return Response({'error': 'User not active, contact support'}, status=403)
            
            if not user.check_password(password):
                return Response({'error': 'Invalid credentials'}, status=400)

            refresh = RefreshToken.for_user(user)
            token = refresh.access_token

            return Response({
                'access': str(token),
                'refresh': str(refresh),
                'email': user.email,
                'name': getattr(user, 'name', '') or '',
                'role': getattr(getattr(user, 'role', None), 'name', '') or ''
            }, status=200)

        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)