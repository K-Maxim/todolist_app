from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView

from core.models import User
from core.serializer import UserRegistrationSerializer


class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
