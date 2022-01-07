from django.db import models
from contacts.models import User


class Shop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    filename = models.CharField(max_length=255)
    is_closed = models.BooleanField(verbose_name='Статус заказов', default=False)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ['-name']
