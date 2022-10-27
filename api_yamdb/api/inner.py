from django.urls import path
from .views import GetToken, RegistrationNewUser


urlpatterns = [
    path('signup/', RegistrationNewUser.as_view(), name='signup'),
    path('token/', GetToken.as_view(), name='token'),
]
