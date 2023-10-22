from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator
from versatileimagefield.fields import VersatileImageField

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


def get_path_image(instance, filename):
    exe = filename.split('.')[-1]
    if isinstance(instance, User):
        email = instance.email
        return f'image/user_image/{email}.{exe}'
    if isinstance(instance, ProductInfo):
        external_id = instance.external_id
        return f'image/products_image/{external_id}.{exe}'


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if self.model.objects.filter(social_auth__user=user).first():
            user.is_active = True
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
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    image = VersatileImageField(
        verbose_name='Аватарка',
        upload_to=get_path_image,
        blank=True,
        null=True,
        default='image/user_image/default_image.png',
        help_text=_('Max size image up to 800x800')
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=60, verbose_name='Название')
    url = models.URLField(max_length=250, null=True, blank=True, verbose_name='Ссылка')
    state = models.BooleanField(default=True, verbose_name='статус получения заказов')
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, null=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ShopImport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='imports',
                             verbose_name='Пользователь')
    yml_url = models.URLField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Импорт товаров'
        verbose_name_plural = 'Импорты товаров'
        ordering = ('-date_added',)

    def __str__(self):
        return self.date_added.strftime("%m/%d/%Y %I:%M:%S %p")


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины', blank=True)
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Лист категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True,
                                 verbose_name='Категория')
    name = models.CharField(max_length=60, verbose_name='Название')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', related_name='product_infos')
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', blank=True,
                             related_name='product_infos')
    quantity = models.PositiveIntegerField(verbose_name='Кол-во')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендованная розничная цена')
    model = models.CharField(max_length=40, blank=True, verbose_name='Модель')
    photo = VersatileImageField(
        upload_to=get_path_image,
        blank=True,
        null=True,
        verbose_name='Фото',
        default='image/products_image/default_product_image.jpg',
        help_text=_('Max image size up to 800x800')
    )

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product_info'),
        ]

    def __str__(self):
        return self.product.__str__()


class Parameter(models.Model):
    name = models.CharField(max_length=60, verbose_name='Название')

    class Meta:
        verbose_name = 'Параметры'
        verbose_name_plural = 'Лист параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, verbose_name='Информация продукта',
                                     blank=True, related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, verbose_name='Параметр', blank=True,
                                  related_name='product_parameters')
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметры продукта'
        verbose_name_plural = 'Параметры продуктов'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]

    def __str__(self):
        return f'Параметры: {self.product_info}'


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='contacts',
                             verbose_name='Пользователь')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, blank=True, verbose_name='Дом')
    structure = models.CharField(max_length=15, blank=True, verbose_name='Корпус')
    building = models.CharField(max_length=15, blank=True, verbose_name='Строение')
    apartment = models.CharField(max_length=15, blank=True, verbose_name='Квартира')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=STATE_CHOICES, verbose_name='Статус', max_length=15)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Контакты')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-dt',)

    def __str__(self):
        return self.dt.strftime("%m/%d/%Y %I:%M:%S %p")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, verbose_name='Заказ',
                              related_name='ordered_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, blank=True,
                                     verbose_name='Информация о заказе', related_name='ordered_items')
    quantity = models.PositiveIntegerField(verbose_name='Кол-во')

    class Meta:
        verbose_name = 'Заказная позиция'
        verbose_name_plural = 'Список заказных позиций'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')
        ]

    def __str__(self):
        return f'Заказ №{self.id}'


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
