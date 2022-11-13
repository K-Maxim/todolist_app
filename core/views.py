from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.exceptions import ValidationError

from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serializer import UserSignupSerializer, UserLoginSerializer, UserProfileSerializer, UserUpdateSerializer


class UserSignupView(CreateAPIView):
    serializer_class = UserSignupSerializer


class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.data
        login(request=request, user=user)
        return Response(UserLoginSerializer(user).data, status=status.HTTP_201_CREATED)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserUpdatePassword(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



