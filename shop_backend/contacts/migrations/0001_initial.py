# Generated by Django 3.2.9 on 2022-01-06 09:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('middle_name', models.CharField(max_length=50, verbose_name='Отчество')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('company', models.CharField(max_length=50, verbose_name='Компания')),
                ('position', models.CharField(max_length=50, verbose_name='Позиция')),
                ('role', models.CharField(choices=[('C', 'Клиент'), ('S', 'Поставщик'), ('A', 'Администратор')], max_length=8, verbose_name='Тип пользователя')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Список пользователей',
                'ordering': ['email'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50, verbose_name='Город')),
                ('street', models.CharField(max_length=50, verbose_name='Улица')),
                ('house', models.CharField(blank=True, max_length=10, verbose_name='Дом')),
                ('building', models.CharField(blank=True, max_length=10, verbose_name='Строение')),
                ('structure', models.CharField(blank=True, max_length=10, verbose_name='Корпус')),
                ('apartment', models.CharField(blank=True, max_length=10, verbose_name='Квартира')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Контакты пользователя',
                'verbose_name_plural': 'Список контактов пользователей',
            },
        ),
    ]
