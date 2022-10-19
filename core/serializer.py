from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from core.models import User


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)


class UserSignupSerializer(serializers.ModelSerializer):

    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    def valid_password(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError('Пароли не совпадают')
        return data

    def create(self, validated_data):
        del validated_data['password_repeat']
        user = User.objects.create(**validated_data)
        user.set_password(user.password)
        user.save()

        return user

    def valid_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя пользователя уже существует')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    def create(self, validated_data):
        user = authenticate(
            username=validated_data['username'],
            password=validated_data['password']
        )
        if not user:
            raise AuthenticationFailed
        return user

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserUpdateSerializer(serializers.ModelSerializer):
    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    def create(self, validated_data: dict):
        return NotImplementedError

    def validate_new_password(self, value):
        validate_password(value)
        return value
