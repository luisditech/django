from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HomologationRule
from .serializers import HomologationRuleSerializer
from django.shortcuts import get_object_or_404

class HomologationRuleListCreateAPIView(APIView):
    def get(self, request):
        rules = HomologationRule.objects.all()
        serializer = HomologationRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HomologationRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class HomologationRuleDetailAPIView(APIView):
    def get(self, request, pk):
        rule = get_object_or_404(HomologationRule, pk=pk)
        serializer = HomologationRuleSerializer(rule)
        return Response(serializer.data)