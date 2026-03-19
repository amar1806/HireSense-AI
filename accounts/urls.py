from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view),
    path('signup', views.signup_view),
    path('verify-otp', views.verify_otp),
    path('logout', views.logout_view),
]