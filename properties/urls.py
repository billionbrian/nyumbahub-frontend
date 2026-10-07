from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet
from payments.views import initiate_payment

router = DefaultRouter()
router.register(r'', PropertyViewSet, basename='property')

urlpatterns = [
    path('pay/', initiate_payment, name='initiate_payment'),
    path('', include(router.urls)),
]
