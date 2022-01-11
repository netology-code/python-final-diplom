from django.db import models
from shops.models import Shop


class Category(models.Model):
    shops = models.ManyToManyField(Shop, through='ShopCategory', related_name='categories', blank=True,
                                   verbose_name='Список магазинов')
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ['-name']


class ShopCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, verbose_name='Магазин')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, verbose_name='Категория')
    internal_category_id = models.PositiveIntegerField(verbose_name='Внутренний идентификатор категории')

    class Meta:
        verbose_name = 'Магазин и категория'
        verbose_name_plural = 'Список магазинов и категорий'
        constraints = [models.UniqueConstraint(fields=['shop', 'category'], name='unique_shop_category')]
