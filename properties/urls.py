from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, initiate_payment

router = DefaultRouter()
router.register(r'', PropertyViewSet, basename='property')

urlpatterns = [
    path('', include(router.urls)),
    path('pay/', initiate_payment, name='initiate_payment'),
]
