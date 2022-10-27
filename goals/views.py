from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment
from goals.serializer import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, GoalSerializer, \
    GoalCommentsCreateSerializer, GoalCommentsSerializer


class GoalCategoryCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCategorySerializer
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(
            user=self.request.user, is_deleted=False
            )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            goal = Goal.objects.filter(category=instance.id)
            goal.status = 4
            instance.save(update_fields=('is_delete', ))
        return instance


class GoalCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
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
        return Goal.objects.filter(
            Q(user_id=self.request.user.id) & ~Q(status=Goal.Status.archived),
            user=self.request.user, is_deleted=False
            )


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(
            Q(user_id=self.request.user.id) & ~Q(status=Goal.Status.archived),
            user=self.request.user, is_deleted=False
            )


class GoalCommentCreateView(CreateAPIView):
    serializer_class = GoalCommentsCreateSerializer
    permission_classes = [IsAuthenticated]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCommentsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ['goal']
    ordering = ["-created"]

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [IsAuthenticated]
    serializer_class = GoalCommentsSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id
        )