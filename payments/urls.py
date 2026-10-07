from django.urls import path
from .views import initiate_payment, mpesa_callback, payment_status, simulate_callback

urlpatterns = [
    path('initiate/', initiate_payment, name='payment_initiate'),
    path('stk-push/', initiate_payment, name='payment_stk_push'),
    path('callback/', mpesa_callback, name='payment_callback'),
    path('status/<str:checkout_request_id>/', payment_status, name='payment_status'),
    path('simulate-callback/', simulate_callback, name='payment_simulate_callback'),
]
