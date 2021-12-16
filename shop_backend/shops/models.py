from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    filename = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ['-name']
