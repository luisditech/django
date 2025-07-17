from django.urls import path
from .views import ConnectionListCreateAPIView, ConnectionDetailAPIView
from .api_connections_views import test_connection_logic

urlpatterns = [
    path('', ConnectionListCreateAPIView.as_view(), name='connection-list-create'),
    path('<int:pk>/', ConnectionDetailAPIView.as_view(), name='connection-detail'),
    path('test/', test_connection_logic, name='connection-test'),
]