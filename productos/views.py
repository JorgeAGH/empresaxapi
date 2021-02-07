from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import StorageSerializer
from .models import Storage
from rest_framework import permissions
from .permissions import IsOwner

class StorageListAPIView(ListCreateAPIView):
    serializer_class = StorageSerializer
    queryset = Storage.objects.all()
    permission_classes=(permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

class StorageDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StorageSerializer
    queryset = Storage.objects.all()
    permission_classes=(permissions.IsAuthenticated, IsOwner,)
    lookup_field='id'

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
