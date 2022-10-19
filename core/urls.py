from django.urls import path

from core import views

urlpatterns = [
    path('signup', views.UserSignupView.as_view(), name='signup'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('profile', views.UserProfileView.as_view(), name='ret-up-dest'),
    path('update_password', views.UserUpdatePassword.as_view(), name='update-pass')
    ]
