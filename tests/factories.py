import factory.django

from core.models import User
from goals.models import Board, GoalCategory, Goal, GoalComment, BoardParticipant


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('name')
    first_name = 'test_first_name'
    last_name = 'test_last_name'
    email = 'test_email@mail.ru'
    password = 'test_password'


class BoardFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('name')
    is_deleted = False

    class Meta:
        model = Board


class BoardParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BoardParticipant

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    role = 1


class GoalCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalCategory

    title = 'test_category'

    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)
    is_deleted = False


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    title = 'test_goal'
    description = 'test_description'
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    status = 1
    priority = 2



class GoalCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalComment

    text = 'test_text'
    goal = factory.SubFactory(GoalFactory)
    user = factory.SubFactory(UserFactory)
