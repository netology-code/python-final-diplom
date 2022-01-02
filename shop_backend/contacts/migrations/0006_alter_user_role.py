# Generated by Django 3.2.9 on 2022-01-02 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_user_is_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('C', 'Клиент'), ('S', 'Поставщик'), ('A', 'Администратор')], max_length=8, verbose_name='Тип пользователя'),
        ),
    ]
