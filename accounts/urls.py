from django.urls import path
from .views import signup, LoginView, current_user

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', current_user, name='current_user'),
]
