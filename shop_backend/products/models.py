from django.db import models
from categories.models import Category
from shops.models import Shop


class Product(models.Model):
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True,
                                   verbose_name='Список категорий')
    shops = models.ManyToManyField(Shop, through='ProductInfo', blank=True, verbose_name='Список магазинов')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ['-name']


class ProductInfo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices', blank=True,
                                verbose_name='Продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Список информации о продуктах'
        constraints = [models.UniqueConstraint(fields=['shop', 'product'], name='unique_product_info')]


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя')
    products = models.ManyToManyField(Product, through='ParameterValue', blank=True, verbose_name='Список продуктов')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметров'
        ordering = ['-name']


class ParameterValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters', blank=True,
                                verbose_name='Продукт')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='values', blank=True,
                                  verbose_name='Параметр')
    value = models.CharField(max_length=50, verbose_name='Значение')

    class Meta:
        verbose_name = 'Продукт и его параметр'
        verbose_name_plural = 'Список продуктов и их параметров'
        constraints = [models.UniqueConstraint(fields=['product', 'parameter'], name='unique_product_parameter')]
