import pytest

from goals.serializer import GoalSerializer
from tests.factories import GoalFactory


@pytest.mark.django_db
def test_goal_create(client, user_access, user, goal_category, board_participant):
    """Создание цели"""
    data = {
        'title': 'test_category',
        'description': 'description',
        'user': user.username,
        'category': goal_category.id,
        'status': 2,
        'priority': 3,
    }

    response = client.post(
        path='/goals/goal/create',

        data=data,
        HTTP_AUTHORIZATION=user_access,
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['description'] == data['description']
    assert response.data['category'] == data['category']
    assert response.data['status'] == data['status']
    assert response.data['priority'] == data['priority']



@pytest.mark.django_db
def test_goal_list(client, user_access, board_participant, goal_category):
    """Список целей"""
    goals = GoalFactory.create_batch(10, user=board_participant.user, category=goal_category)

    response = client.get(
        path='/goals/goal/list',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalSerializer(goals, many=True).data


@pytest.mark.django_db
def test_goal_retrieve(client, user_access, goal, user, board_participant):
    """Просмотр цели"""
    response = client.get(
        path=f'/goals/goal/{goal.id}',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalSerializer(goal).data

# DONE!!!
@pytest.mark.django_db
def test_goal_update(client, user_access, goal, board_participant):
    """Обновление цели"""
    new_title = 'updated_title'

    response = client.patch(
        path=f'/goals/goal/{goal.id}',
        HTTP_AUTHORIZATION=user_access,
        data={'title': new_title},
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.data.get('title') == new_title

# DONE!!!
@pytest.mark.django_db
def test_goal_delete(client, user_access, goal, board_participant):
    """Удаление цели"""
    response = client.delete(
        path=f'/goals/goal/{goal.id}',
        HTTP_AUTHORIZATION=user_access,
    )

    assert response.status_code == 204
    assert response.data is None
