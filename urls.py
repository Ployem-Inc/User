"""
user url patterns
"""
from django.urls import path
from . import views

urlpatterns = [
    path("signup", views.sign_up, name = "user-signup"),
    path("signin", views.sign_in, name = "user-signin"),
    path("send-verify", views.send_verify, name = "send-verify"),
    path("signout", views.sign_out, name = "user-signout"),
    path("confirm-verify", views.confirm_verify, name = "confirm-verify"),
]