from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Информация о пользователе')
    middle_name = models.CharField(max_length=50, verbose_name='Отчество')
    company = models.CharField(max_length=50, verbose_name='Компания')
    position = models.CharField(max_length=50, verbose_name='Позиция')


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', blank=True,
                             verbose_name='Пользователь')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=50, verbose_name='Улица')
    house = models.CharField(max_length=10, blank=True, verbose_name='Дом')
    building = models.CharField(max_length=10, blank=True, verbose_name='Строение')
    structure = models.CharField(max_length=10, blank=True, verbose_name='Корпус')
    apartment = models.CharField(max_length=10, blank=True, verbose_name='Квартира')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователей"
