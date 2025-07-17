from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from apps.authentication.views import ForgotPasswordView
from django.conf.urls.static import static
# 👇 Agregamos el esquema de seguridad para JWT (Bearer)
schema_view = get_schema_view(
    openapi.Info(
        title="Orchestrator API",
        default_version='v1',
        description="Interactive documentation for the Orchestrator API",
        contact=openapi.Contact(email="tu@empresa.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    
    # 🔐 Endpoints de autenticación JWT
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('apps.users.urls')),
    path('', include('apps.authentication.urls')),
    path('api/connections/', include('apps.connections.urls')),
    # path('api/operations/', include('apps.operations.urls')),
    path('api/homologations/', include('apps.homologations.urls')),
    # 📄 Swagger UI
    path('', include('apps.workflows.urls')),
    path('api/', include('apps.works.urls')),
    path('api/', include('apps.workExecution.urls')),
    path("api/", include("apps.workExecutionList.urls")),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # 🧩 Módulos por negocio
    # path('api/custom_app_example/', include('apps.buencapital.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
