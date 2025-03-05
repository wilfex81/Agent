from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationAPIView,

)
urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user_register'),

]