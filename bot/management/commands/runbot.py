import os

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.models import Message
from todolist import settings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

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

    def handle_massage(self, message: Message):
        tg_user, _ = TgUser.objects.select_related('user').get_or_create(
            chat_id=message.chat.id,
            defaults={
                'username': message.from_.username
            }
        )
        if tg_user.user:
            self.tg_client.send_message(chat_id=message.chat.id, text='Вы уже зарегистрированы')
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
