from django.urls import path
from .views import StorageListAPIView, StorageDetailsAPIView

urlpatterns = [
    path('',StorageListAPIView.as_view(), name='storage'),
    path('<int:id>',StorageDetailsAPIView.as_view(), name='storage')
]