# homologation/serializers.py
from rest_framework import serializers
from .models import HomologationRule

class HomologationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomologationRule
        fields = '__all__'