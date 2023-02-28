from pprint import pprint

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
# from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from orders.serializers import UserSerializer, ContactSerializer
from orders.models import User, ConfirmEmailToken, Contact


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):

            # проверяем пароль на сложность

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Подтверждение регистрации
    """
    permission_classes = [AllowAny]

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data['email'], is_active=True)
        if user:
            return JsonResponse({'Status': 200, 'Message': _('Confirmation has been done earlier')})

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                # reset_password_token_created.send(sender=self.__class__, user_id=user.id)
                token.delete()
                return JsonResponse({'Status': 200, 'Message': _('Registration complete successfully')})
            else:
                return JsonResponse({'Status': 403, 'Errors': _('Неправильно указан токен или email')})

        return JsonResponse({'Status': 411, 'Errors': 'Не указаны все необходимые аргументы'})


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()

    def get_queryset(self):
        """
        This view should return CRUD of all the contacts
        for the currently authenticated user.
        """
        return super().get_queryset().filter(user_id=self.request.user)

    def create(self, request, *args, **kwargs):
        contact_data = self.request.data
        # change request data so that it's mutable, otherwise this will raise
        # a "This QueryDict instance is immutable." error
        contact_data._mutable = True
        # set the requesting user ID for the User ForeignKey
        contact_data['user'] = self.request.user.id

        print('comment_data')
        pprint(contact_data)

        serializer = ContactSerializer(data=contact_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
