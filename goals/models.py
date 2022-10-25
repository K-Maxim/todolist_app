from django.db import models
from django.utils import timezone

from core.models import User


class BaseModel(models.Model):
    created = models.DateTimeField(verbose_name="Дата создания", auto_now=True)
    updated = models.DateTimeField(verbose_name="Дата последнего обновления", auto_now=True)

    class Meta:
        abstract = True


class GoalCategory(BaseModel):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    def __str__(self):
        return self.title

