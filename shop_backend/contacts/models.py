from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    middle_name = models.CharField(max_length=50, verbose_name='Отчество')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(max_length=50, verbose_name='Пароль')
    company = models.CharField(max_length=50, verbose_name='Компания')
    position = models.CharField(max_length=50, verbose_name='Позиция')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ['-email']


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
