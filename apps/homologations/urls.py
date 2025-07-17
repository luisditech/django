# homologation/urls.py
from django.urls import path
from .views import HomologationRuleListCreateAPIView, HomologationRuleDetailAPIView

urlpatterns = [
    path('rules/', HomologationRuleListCreateAPIView.as_view()),
    path('rules/<int:pk>/', HomologationRuleDetailAPIView.as_view()),
]