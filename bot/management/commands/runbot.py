import logging
import os
from datetime import datetime

from django.core.management import BaseCommand
from enum import IntEnum, auto

from pydantic import BaseModel

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.fsm.memory_storage import MemoryStorage
from bot.tg.models import Message
from goals.models import Goal, GoalCategory, BoardParticipant
from todolist import settings

logger = logging.getLogger(__name__)


class NewGoal(BaseModel):
    cat_id: int | None = None
    goal_title: str | None = None

    @property
    def is_completed(self) -> bool:
        return None not in [self.cat_id, self.goal_title]


class StateEnum(IntEnum):
    CREATE_CATEGORY_SELECT = auto
    CHOSEN_CATEGORY = auto


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)
        self.storage = MemoryStorage()

    @staticmethod
    def _generate_verification_code():
        return os.urandom(12).hex()

    def handle_unverified_user(self, massage: Message, tg_user: TgUser):
        code: str = self._generate_verification_code()
        tg_user.verification_code = code
        tg_user.save(update_fields=('verification_code',))
        self.tg_client.send_message(
            chat_id=massage.chat.id,
            text=f"[verification_code] {tg_user.verification_code}"
        )

    def handle_goals_list(self, message: Message, tg_user: TgUser):
        response_goals: list[str] = [
            f"#{goal.id} {goal.title}"
            for goal in Goal.objects.filter(user_id=tg_user.user.id).order_by('created')
        ]
        if response_goals:
            self.tg_client.send_message(message.chat.id, "\n".join(response_goals))
        else:
            self.tg_client.send_message(message.chat.id, "[you have no goals]")

    def handle_goals_categories_list(self, message: Message, tg_user: TgUser):
        response_categories: list[str] = [
            f"#{cat.id} {cat.title}"
            for cat in GoalCategory.objects.filter(
                board__participants__user_id=tg_user.user_id,
                is_deleted=False
            )
        ]
        if response_categories:
            self.tg_client.send_message(message.chat.id, "Select category:\n" + "\n".join(response_categories))
        else:
            self.tg_client.send_message(message.chat.id, "[you have no categories]")

    def handle_save_selected_category(self, massage: Message, tg_user: TgUser):
        if massage.text.isdigit():
            cat_id = int(massage.text)
            if GoalCategory.objects.filter(
                    board__participants__user_id=tg_user.user_id,
                    board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                    is_deleted=False,
                    id=cat_id
            ).exists():
                self.storage.update_data(chat_id=massage.chat.id, cat_id=cat_id)
                self.tg_client.send_message(massage.chat.id, '[set title]')
                self.storage.set_state(massage.chat.id, state=StateEnum.CHOSEN_CATEGORY)
            else:
                self.tg_client.send_message(massage.chat.id, '[Category is not found]')
        else:
            self.tg_client.send_message(massage.chat.id, '[Invalid category id]')

    def handle_save_new_cat(self, message: Message, tg_user: TgUser):
        goal = NewGoal(**self.storage.get_data(tg_user.chat_id))
        goal.goal_title = message.text
        if goal.is_completed:
            Goal.objects.create(
                title=goal.goal_title,
                category_id=goal.cat_id,
                user_id=tg_user.user_id,
                due_date=datetime.now()
            )
            self.tg_client.send_message(message.chat.id, '[New goal created]')
        else:
            #TODO: Log
            self.tg_client.send_message(message.chat.id, '[something went mistake]')
        self.storage.reset(tg_user.chat_id)

    def handle_verified_user(self, massage: Message, tg_user: TgUser):
        if massage.text == '/goals':
            self.handle_goals_list(massage, tg_user)

        elif massage.text == '/create':
            self.handle_goals_categories_list(massage, tg_user)
            self.storage.set_state(massage.chat.id, state=StateEnum.CREATE_CATEGORY_SELECT)
            self.storage.set_data(massage.chat.id, data=NewGoal().dict())

        elif massage.text == '/cancel' and self.storage.get_state(tg_user.chat_id):
            self.storage.reset(tg_user.chat_id)
            self.tg_client.send_message(massage.chat.id, '[canceled]')

        elif state := self.storage.get_state(tg_user.chat_id):
            match state:
                case StateEnum.CREATE_CATEGORY_SELECT:
                    self.handle_save_selected_category(massage, tg_user)
                case StateEnum.CHOSEN_CATEGORY:
                    self.handle_save_new_cat(massage, tg_user)
                case _:
                    logger.warning("Invalid state", state)

        elif massage.text.startswith('/'):
            self.tg_client.send_message(massage.chat.id, '[unknown command]')

    def handle_massage(self, message: Message):
        tg_user, _ = TgUser.objects.select_related('user').get_or_create(
            chat_id=message.chat.id,
            defaults={
                'username': message.from_.username
            }
        )
        if tg_user.user:
            self.handle_verified_user(massage=message, tg_user=tg_user)
        else:
            self.handle_unverified_user(massage=message, tg_user=tg_user)

    def handle(self, *args, **options):
        offset = 0
        tg_client = TgClient(settings.BOT_TOKEN)
        while True:
            res = tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_massage(message=item.message)
