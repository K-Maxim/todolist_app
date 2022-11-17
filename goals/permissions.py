from rest_framework import permissions

from goals.models import BoardParticipant, GoalCategory, Board, Goal


class BoardPermissions(permissions.IsAuthenticated):
    """Доступ к работе на доске (авторизованному владельцу)"""
    def has_object_permission(self, request, view, obj: Board):
        filters: dict = {'user': request.user, 'board': obj}
        if request.method not in permissions.SAFE_METHODS:
            filters['role'] = BoardParticipant.Role.owner
        return BoardParticipant.objects.filter(**filters).exists()


class GoalCategoryPermissions(permissions.IsAuthenticated):
    """Доступ к работе с категориями (авторизованному владельцу и редактору)"""
    def has_object_permission(self, request, view, obj: GoalCategory):
        filters: dict = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermissions(permissions.IsAuthenticated):
    """Доступ к работе с целями (авторизованному владельцу и редактору)"""
    def has_object_permission(self, request, view, obj: Goal):
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj.category.board
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj.category.board,
            role__in=(BoardParticipant.Role.owner, BoardParticipant.Role.writer)
        ).exists()


class CommentPermissions(permissions.IsAuthenticated):
    """Доступ к комментариям"""
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id
