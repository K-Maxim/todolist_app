import pytest

from core.serializer import UserProfileSerializer


@pytest.mark.django_db
def test_user_create(client, django_user_model):
    """Тест создания пользователя"""
    data = {
        'username': 'Tester',
        'password': 'Password8956',
        'password_repeat': 'Password8956',
    }

    response = client.post(
        path='/core/signup',
        data=data,
        content_type='application/json'
    )

    user = django_user_model.objects.first()

    expected_response = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }

    assert response.status_code == 201
    assert response.data == expected_response


@pytest.mark.django_db
def test_user_login(client, user):
    """Тест авторизации пользователя"""
    password = user.password

    user.set_password(password)
    user.save()

    response = client.post(
        path='/core/login',
        data={
            'username': user.username,
            'password': password,
        },
        content_type='application/json'
    )

    expected_response = {
        'username': user.username,
        'last_name': user.last_name,
        'email': user.email,
        'first_name': user.first_name,

    }

    assert response.status_code == 201
    assert response.data == expected_response


@pytest.mark.django_db
def test_user_profile(client, user_access, user):
    """Тест просмотра профиля"""
    response = client.get(
        path='/core/profile',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == UserProfileSerializer(user).data


@pytest.mark.django_db
def test_update_password(client, user_access):
    response = client.put(
        path='/core/update_password',
        HTTP_AUTHORIZATION=user_access,
        data={
            'old_password': 'test_password',
            'new_password': 'dj%#!dfsd%$w923',
        },
        content_type='application/json'
    )

    assert response.status_code == 200
