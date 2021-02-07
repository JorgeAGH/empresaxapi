from django.urls import path
from .views import IncomeListAPIView, IncomeDetailsAPIView

urlpatterns = [
    path('',IncomeListAPIView.as_view(), name='income'),
    path('<int:id>',IncomeDetailsAPIView.as_view(), name='income')
]