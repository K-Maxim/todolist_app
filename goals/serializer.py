from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from core.models import User
from core.serializer import UserProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания категории"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, value: Board):
        if value.is_deleted:
            raise serializers.ValidationError('Нельзя удалить категорию')
        if not BoardParticipant.objects.filter(board=value,
                                               role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                                               user=self.context['request'].user
                                               ).exists():
            raise serializers.ValidationError('Нет доступа')
        return value

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", 'is_deleted')

        fields = '__all__'


class GoalCategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для показа категорий/категории"""
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "board")


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания цели"""
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_category(self, value: GoalCategory):
        if self.context['request'].user != value.user:
            return PermissionError

        if not BoardParticipant.objects.filter(
                board_id=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user=self.context['request'].user,
        ).exists():
            raise PermissionDenied

        return value

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalSerializer(serializers.ModelSerializer):
    """Сералайзер для показа целей/цели"""
    category = serializers.PrimaryKeyRelatedField(
        queryset=GoalCategory.objects.filter(is_deleted=False)
    )

    def validate_category(self, value):
        if self.context['request'].user != value.user:
            return PermissionError
        return value

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentsCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания комментария"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


class GoalCommentsSerializer(serializers.ModelSerializer):
    """Сериалайзер для показа комментариев/комментария"""
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user", "goal")

        fields = "__all__"


class BoardCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания доски"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Сериалайзер для участников доски"""
    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.Role.choices
    )
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    """Сериалайзер для одной доски (показ, обновление, удаление)"""
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, instance, validated_data):
        if validated_data.get("participants"):
            new_participants = validated_data.pop("participants")
            new_by_id = {part["user"].id: part for part in new_participants}

            old_participants = instance.participants.exclude(user=self.context.get('request').user)
            with transaction.atomic():
                for old_participant in old_participants:
                    if old_participant.user_id not in new_by_id:
                        old_participant.delete()
                    else:
                        if (
                                old_participant.role
                                != new_by_id[old_participant.user_id]["role"]
                        ):
                            old_participant.role = new_by_id[old_participant.user_id][
                                "role"
                            ]
                            old_participant.save()
                        new_by_id.pop(old_participant.user_id)
                for new_part in new_by_id.values():
                    BoardParticipant.objects.create(
                        board=instance, user=new_part["user"], role=new_part["role"]
                    )
                if title := validated_data["title"]:
                    instance.title = title
                    instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Сериалайзер для показа всех досок"""

    class Meta:
        model = Board
        fields = "__all__"
