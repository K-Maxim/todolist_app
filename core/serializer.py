from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from core.models import User


class PasswordField(serializers.CharField):
    """Валидация пароля"""
    def __init__(self, **kwargs):
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)


class UserSignupSerializer(serializers.ModelSerializer):
    """Создание пользователя"""
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
    """Аутентификация пользователя"""
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    def create(self, validated_data):
        if not (user := authenticate(
                username=validated_data['username'],
                password=validated_data['password']
        )):
            raise AuthenticationFailed
        return user

    class Meta:
        model = User
        fields = ('username', 'password', 'last_name', 'email', 'first_name')


class UserProfileSerializer(serializers.ModelSerializer):
    """Профиль пользователя"""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserUpdateSerializer(serializers.Serializer):
    """Смена пароля"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    def create(self, validated_data: dict):
        return NotImplementedError

    def validate(self, data: dict):
        if not (user := data.get('user')):
            raise NotAuthenticated
        if not user.check_password(data['old_password']):
            raise ValidationError({'old_password': 'пароль некорректный'})
        return data

    def update(self, instance: User, validated_data: dict) -> User:
        instance.password = make_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance
