from django.db import transaction
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalPermissions, CommentPermissions
from goals.serializer import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, GoalSerializer, \
    GoalCommentsCreateSerializer, GoalCommentsSerializer, BoardCreateSerializer, BoardSerializer, BoardListSerializer


class BoardCreateView(CreateAPIView):
    """Создание доски"""
    permission_classes = [BoardPermissions]
    serializer_class = BoardCreateSerializer


class BoardListView(ListAPIView):
    """Список всех доск"""
    model = Board
    permission_classes = [BoardPermissions]
    serializer_class = BoardListSerializer
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(participants__user_id=self.request.user.id,
                                                                     is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """Одна доска (показ, обновление, удаление)"""
    model = Board
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(participants__user_id=self.request.user.id,
                                                                     is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=("is_deleted",))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class GoalCategoryCreateView(CreateAPIView):
    """Создание категории"""
    model = GoalCategory
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """Список всех категорий"""
    model = GoalCategory
    permission_classes = [GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    filterset_fields = ['board']
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user_id=self.request.user,
            user=self.request.user,
            is_deleted=False,
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """Одна категория (показ, обновление, удаление)"""
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user_id=self.request.user.id, is_deleted=False
        )

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        return instance


class GoalCreateView(CreateAPIView):
    """Создание цели"""
    model = GoalCategory
    permission_classes = [GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """Список всех целей"""
    model = Goal
    permission_classes = [IsAuthenticated]
    serializer_class = GoalSerializer
    filterset_class = GoalDateFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived),
        )


class GoalView(RetrieveUpdateDestroyAPIView):
    """Одна цель (показ, обновление, удаление)"""
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [GoalPermissions]

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived)
        )

    def perform_destroy(self, instance: Goal):
        instance.Status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class GoalCommentCreateView(CreateAPIView):
    """Добавление комментария"""
    serializer_class = GoalCommentsCreateSerializer
    permission_classes = [CommentPermissions]


class GoalCommentListView(ListAPIView):
    """Список всех комментариев"""
    model = GoalComment
    permission_classes = [CommentPermissions]
    serializer_class = GoalCommentsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ['goal']
    ordering = ["-created"]

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """Один комментарий (показ, обновление, удаление)"""
    model = GoalComment
    permission_classes = [CommentPermissions]
    serializer_class = GoalCommentsSerializer

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id
        )
