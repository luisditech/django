from django.urls import path
from .views import (
    WorkListCreateAPIView,
    WorkDetailAPIView,
    WorkRunAPIView,
)

urlpatterns = [
    path('works', WorkListCreateAPIView.as_view(), name='work-list'),
    path('works/<int:pk>/', WorkDetailAPIView.as_view(), name='work-detail'),
    path('works/<int:pk>/run/', WorkRunAPIView.as_view(), name='work-run'),
]
