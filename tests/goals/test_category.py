import pytest

from goals.serializer import GoalCategorySerializer, GoalCategoryCreateSerializer
from tests.factories import GoalCategoryFactory, BoardParticipantFactory


@pytest.mark.django_db
def test_category_create(client, user_access, user, board):
    """Создание категории"""
    data = GoalCategoryFactory.create_batch(1)
    data = data[0]
    user = BoardParticipantFactory.role

    data = {
        'title': data.board.title,
        'user': user,
        'board': data.board.id,
    }

    response = client.post(
        path='/goals/goal_category/create',
        data=data,
        HTTP_AUTHORIZATION=user_access,
        content_type='application/json',
    )

    assert response.data == data
    assert response.status_code == 201



# DONE!!!
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


# DONE!!!
@pytest.mark.django_db
def test_category_retrieve(client, user_access, goal_category, board_participant):
    """Просмотр категории"""

    response = client.get(
        path=f'/goals/goal_category/{goal_category.id}',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalCategorySerializer(goal_category).data


# DONE!!!
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


# DONE!!!
@pytest.mark.django_db
def test_category_delete(client, user_access, goal_category, board_participant):
    """Удаление категории"""
    response = client.delete(
        path=f'/goals/goal_category/{goal_category.id}',
        HTTP_AUTHORIZATION=user_access,
    )

    assert response.status_code == 204
    assert response.data is None
