# Generated by Django 3.2.9 on 2022-01-01 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Имя')),
            ],
            options={
                'verbose_name': 'Параметра',
                'verbose_name_plural': 'Список параметров',
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='categories.category', verbose_name='Список категорий')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Список продуктов',
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('price_rrc', models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')),
                ('product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='products.product', verbose_name='Продукт')),
                ('shop', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shops.shop')),
            ],
            options={
                'verbose_name': 'Информация о продукте',
                'verbose_name_plural': 'Список информации о продуктах',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='shops',
            field=models.ManyToManyField(blank=True, through='products.ProductInfo', to='shops.Shop', verbose_name='Список магазинов'),
        ),
        migrations.CreateModel(
            name='ParameterValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50, verbose_name='Значение')),
                ('parameter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='values', to='products.parameter', verbose_name='Параметр')),
                ('product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='products.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Продукт и параметр',
                'verbose_name_plural': 'Список продуктов и параметров',
            },
        ),
        migrations.AddField(
            model_name='parameter',
            name='products',
            field=models.ManyToManyField(blank=True, through='products.ParameterValue', to='products.Product', verbose_name='Список продуктов'),
        ),
        migrations.AddConstraint(
            model_name='productinfo',
            constraint=models.UniqueConstraint(fields=('shop', 'product'), name='unique_product_info'),
        ),
        migrations.AddConstraint(
            model_name='parametervalue',
            constraint=models.UniqueConstraint(fields=('product', 'parameter'), name='unique_product_parameter'),
        ),
    ]
