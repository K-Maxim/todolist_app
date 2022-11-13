from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from goals.models import BoardParticipant


class BoardPermissions(permissions.BasePermission):
    """Доступ к работе на доске (авторизованному владельцу)"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class GoalCategoryPermissions(IsAuthenticated):
    """Доступ к работе на доске (авторизованному владельцу и редактору)"""
    def has_object_permission(self, request, view, obj):
        filters: dict = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermissions(IsAuthenticated):
    """Доступ к работе с целями (авторизованному владельцу и редактору)"""
    def has_object_permission(self, request, view, obj):
        filters: dict = {'user': request.user, 'board': obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class CommentPermissions(IsAuthenticated):
    """Доступ к комментариям"""
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id