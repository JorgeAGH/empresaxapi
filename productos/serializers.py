from rest_framework import serializers
from .models import Storage


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['id', 'date', 'descripcion', 'precios', 'category']
        