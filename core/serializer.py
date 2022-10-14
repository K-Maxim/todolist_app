from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    username = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=50, allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    password = serializers.CharField(max_length=50, required=True)
    phone = serializers.CharField(max_length=15, required=False, allow_null=True)

    def check_password(self, value):
        validate_password(value)
        return value

    def valid_password(self, data):
        if data.get('password') == data.get('password_repeat'):
            return data
        raise serializers.ValidationError('Пароли не совпадают')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(user.password)
        user.save()

        return user

    def valid_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Имя пользователя уже существует')

    class Meta:
        model = User
        fields = '__all__'
