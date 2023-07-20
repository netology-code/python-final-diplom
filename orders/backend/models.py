from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class OrderStateChoices(models.TextChoices):
    """Статусы заказа."""
    BASKET = 'basket', 'Статус корзины'
    NEW = 'new' 'Новый'
    CONFIRMED = 'confirmed', 'Подтвержден'
    ASSEMBLED = 'assembled', 'Собран'
    SENT = 'sent', 'Отправлен'
    DELIVERED = 'delivered', 'Доставлен'
    CANCELED ='canceled', 'Отменен'


class UserTypeChoices(models.TextChoices):
    """Типы пользователей."""
    SHOP = 'shop', 'Магазин'
    BUYER = 'buyer', 'Покупатель'


class UserManager(BaseUserManager):
    """Управление пользователями."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Стандартная модель пользователей."""
    REQUIRED_FIELDS = ['email']
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    email = models.EmailField(unique=True, verbose_name='Эл. почта')
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        max_length=150,
        unique=True, 
        verbose_name='username', 
        validators=[username_validator],
        help_text=('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={'unique': ("A user with that username already exists.")},
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Статус', 
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    full_name = models.TextField(max_length=100, null=True, blank=True, verbose_name='Фамилия, имя, отчество')
    type = models.TextField(choices=UserTypeChoices.choices, default=UserTypeChoices.BUYER, verbose_name='Тип пользователя')
    company = models.CharField(max_length=100, null=True, blank=True, verbose_name='Компания')
    position = models.CharField(max_length=100, null=True, blank=True, verbose_name='Должность')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
    
    def __str__(self):
        return f'{self.username}: {self.email}'


class Shop(models.Model):
    """Магазины."""
    name = models.CharField(max_length=40, unique=True, verbose_name='Название')
    url = models.URLField(null=True, blank=True, unique=True, verbose_name='Ссылка')
    filename = models.FileField(null=True, blank=True, verbose_name='Название файла')
    state = models.BooleanField(default=True, verbose_name='Статус')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name}: {self.state}' 


class Category(models.Model):
    """Категории товаров."""
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=40, unique=True, verbose_name='Название')
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True, verbose_name='Магазины')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name 
    

class Product(models.Model):
    """Товары."""
    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name', 'category']
    
    def __str__(self):
        return f'{self.name}: {self.category}'


class ProductInfo(models.Model):
    """Информация о товарах."""
    product = models.ForeignKey(Product, related_name='product_info', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Продукт')
    shop = models.ForeignKey(Shop, related_name='product_info', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Магазин')
    external_id = models.PositiveIntegerField(unique=True, verbose_name='Внешний Id')
    model = models.CharField(max_length=100, verbose_name='Модель')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Информационные листы о товаре'
        ordering = ['product', 'model', 'shop', 'quantity']
        constraints = [models.UniqueConstraint(fields=['product', 'model', 'shop', 'external_id'], name='unique_product_info')]
    
    def __str__(self):
        return self.model 
    

class Parameter(models.Model):
    """Характеристики."""
    name = models.CharField(max_length=40, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Названия параметров'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Товары с характеристиками."""
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Информация о продукте')
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Параметр')
    value = models.CharField(max_length=40, null=True, blank=True, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ['-product_info', '-parameter']
        constraints = [models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')]
    
    def __str__(self):
        return f'{self.parameter}: {self.value}'


class Contact(models.Model):
    """Контактная информация пользователя."""
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE, verbose_name='Пользователь')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', null=True, blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', null=True, blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', null=True, blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'
        ordering = ['user']
    
    def __str__(self):
        return f'{self.user}: {self.city}, {self.street}'


class Order(models.Model):
    """Заказ."""
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    state = models.TextField(choices=OrderStateChoices.choices, verbose_name='Статус')
    contact = models.ForeignKey(Contact, related_name='orders', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Контактная информация')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['user', '-dt', 'state']
    
    def __str__(self): 
        return f'{self.user}: {self.dt}'
    

class OrderItem(models.Model):
    """Позиции в заказе."""
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Заказ')
    product_info = models.ForeignKey(ProductInfo, related_name='order_items', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Информация о продукте')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = 'Позиции в заказе'
        constraints = [models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')]
    
    def __str__(self):
        return f'{self.order}: {self.product_info}'