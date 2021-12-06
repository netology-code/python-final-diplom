from django.db import models
from contacts.models import User
from products.models import ProductInfo


class Order(models.Model):
    STATE_CHOICES = [
        ('assembled', 'Собран'),
        ('basket', 'Статус корзины'),
        ('canceled', 'Отменен'),
        ('confirmed', 'Подтвержден'),
        ('delivered', 'Доставлен'),
        ('new', 'Новый'),
        ('sent', 'Отправлен')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', blank=True,
                             verbose_name='Пользователь')
    products = models.ManyToManyField(ProductInfo, through='OrderContent', blank=True, verbose_name='Список продуктов')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Дата создания')
    status = models.CharField(max_length=15, choices=STATE_CHOICES, verbose_name='Статус')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ['-created_at']


class OrderContent(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, blank=True, verbose_name='Продукт')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', blank=True, verbose_name='Заказ')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Содержимое заказа'
        verbose_name_plural = 'Содержимое заказа'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'order'], name='unique_order_item'),
        ]
