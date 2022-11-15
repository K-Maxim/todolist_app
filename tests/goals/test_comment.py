import pytest

from goals.serializer import GoalCommentsSerializer
from tests.factories import GoalCommentFactory

# DONE!!!
@pytest.mark.django_db
def test_comment_create(client, user_access, goal, board_participant):
    """Создание комментария"""
    data = {
        'text': 'text',
        'goal': goal.id,
    }

    response = client.post(
        path='/goals/goal_comment/create',
        HTTP_AUTHORIZATION=user_access,
        data=data,
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.data['text'] == data['text']
    assert response.data['goal'] == data['goal']

# DONE!!!
@pytest.mark.django_db
def test_comment_list(client, user_access, goal, board_participant):
    """Список комментариев"""
    comments = GoalCommentFactory.create_batch(10, user=goal.user, goal=goal)
    comments.sort(key=lambda x: x.id, reverse=True)

    response = client.get(
        path='/goals/goal_comment/list',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalCommentsSerializer(comments, many=True).data

# DONE!!!
@pytest.mark.django_db
def test_comment_retrieve(client, user_access, goal_comment, board_participant):
    """Просмотр комментария"""
    response = client.get(
        path=f'/goals/goal_comment/{goal_comment.id}',
        HTTP_AUTHORIZATION=user_access
    )

    assert response.status_code == 200
    assert response.data == GoalCommentsSerializer(goal_comment).data

# DONE!!!
@pytest.mark.django_db
def test_comment_update(client, user_access, goal_comment, board_participant):
    """Обновление комментария"""
    new_text = 'updated_text'

    response = client.patch(
        path=f'/goals/goal_comment/{goal_comment.id}',
        HTTP_AUTHORIZATION=user_access,
        data={'text': new_text},
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.data.get('text') == new_text

# DONE!!!
@pytest.mark.django_db
def test_comment_delete(client, user_access, goal_comment, board_participant):
    """Удаление комментария"""
    response = client.delete(
        path=f'/goals/goal_comment/{goal_comment.id}',
        HTTP_AUTHORIZATION=user_access,
    )

    assert response.status_code == 204
    assert response.data is None
