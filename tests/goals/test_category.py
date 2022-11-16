import pytest

from goals.serializer import GoalCategorySerializer
from tests.factories import GoalCategoryFactory


@pytest.mark.django_db
def test_category_create(client, user_access, user, board, board_participant):
    """Создание категории"""

    data = {
        'title': board.title,
        'user': user.id,
        'board': board.id,
    }

    response = client.post(
        path='/goals/goal_category/create',
        data=data,
        HTTP_AUTHORIZATION=user_access,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['board'] == data['board']


@pytest.mark.django_db
def test_category_list(client, user_access, board_participant):
    """Список категорий"""
    categories = GoalCategoryFactory.create_batch(10, user=board_participant.user, board=board_participant.board)

    response = client.get(
        path='/goals/goal_category/list',
        HTTP_AUTHORIZATION=user_access,
    )

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(categories, many=True).data


@pytest.mark.django_db
def test_category_retrieve(client, user_access, goal_category, board_participant):
    """Просмотр категории"""

    response = client.get(
        path=f'/goals/goal_category/{goal_category.id}',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(goal_category).data


@pytest.mark.django_db
def test_category_update(client, user_access, goal_category, board_participant):
    """Обновление категории"""
    new_title = 'updated_title'

    response = client.patch(
        path=f'/goals/goal_category/{goal_category.id}',
        HTTP_AUTHORIZATION=user_access,
        data={'title': new_title},
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.data.get('title') == new_title


@pytest.mark.django_db
def test_category_delete(client, user_access, goal_category, board_participant):
    """Удаление категории"""
    response = client.delete(
        path=f'/goals/goal_category/{goal_category.id}',
        HTTP_AUTHORIZATION=user_access,
    )

    assert response.status_code == 204
    assert response.data is None
