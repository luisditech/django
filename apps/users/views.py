from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import User,Role
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer
from utils.pagination import paginate_queryset
from security.password import check_password_security
from django.db.models import Q
# from apps.common.services.email_service import send_email
from django.conf import settings

class UserAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Get all users",
        responses={200: UserSerializer(many=True)}
    )
    @paginate_queryset(UserSerializer)
    def get(self, request, *args, **kwargs):
        role_param = request.GET.get('role')       
        status_param = request.GET.get('status')   
        query = request.GET.get('q', '').strip()

        queryset = User.objects.filter(is_deleted=False).order_by('id')

        if role_param:
            role_names = [r.strip().capitalize() for r in role_param.split(',')]
            roles = Role.objects.filter(name__in=role_names)
            if roles.exists():
                queryset = queryset.filter(role__in=roles)
            else:
                return User.objects.none()

        if status_param:
            statuses = [s.strip().lower() for s in status_param.split(',')]
            status_filter = Q()

            if "active" in statuses:
                status_filter |= Q(is_active=True, is_blocked=False)
            if "inactive" in statuses:
                status_filter |= Q(is_active=False)
            if "pending" in statuses:
                status_filter |= Q(role__isnull=True)
            if "block" in statuses:
                status_filter |= Q(is_blocked=True)

            queryset = queryset.filter(status_filter)

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query)
            )

        return queryset

    @check_password_security
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: UserSerializer(),
            400: "Invalid data"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            # send_email(
            #     template_name='new_registration_request.html',
            #     context={
            #         'name': user.name,
            #         'email': user.email,
            #         'user_list_url': f"{settings.FRONT_URL}/pruebas/usuarios"
            #     },
            #     to='juancarlos.alvarado@grupoditech.es',
            #     subject='Nueva Solicitud de Registro')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Update an existing user",
        request_body=UserSerializer,
        responses={200: UserSerializer, 404: "User not found"}
    )
    def put(self, request, pk, *args, **kwargs):
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            was_inactive = not user.is_active

            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                updated_user = serializer.save()

                # if was_inactive and updated_user.is_active:
                #     send_email(
                #         template_name='access_approved.html',
                #         context={
                #             'platform_url': f"{settings.FRONT_URL}/login"
                #         },
                #         to=updated_user.email,
                #         subject='Acceso Aprobado - BuenCapital'
                #     )

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a user (logical delete)",
        responses={204: "User deactivated", 404: "User not found"}
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.is_deleted = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)