# from pprint import pprint

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
# from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from orders.send_email import send_email_4_verification
from orders.serializers import UserSerializer, ContactSerializer
from orders.models import User, ConfirmEmailToken, Contact
from orders.permissions import IsOwner


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request,
                                username=request.data['email'],
                                password=request.data['password'])

            if user is not None:
                if not user.email_is_verified:
                    return JsonResponse({
                        'Status': False,
                        'Message': 'Please make an email verification procedure.'},
                        status=status.HTTP_403_FORBIDDEN)

                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key},
                                        status=status.HTTP_200_OK)

            return JsonResponse(
                {'Status': False,
                 'Errors': 'Не удалось авторизовать'})

        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'first_name',
            'last_name', 'email',
            'password', 'company',
            'position'} \
                .issubset(request.data):

            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse(
                    {'Status': False,
                     'Errors': {'password': error_array}},
                    status=status.HTTP_400_BAD_REQUEST)
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
                    # verification of email
                    send_email_4_verification(request, user)
                    return JsonResponse(
                        {'Status': True,
                         'Message':
                             'Check your email to complete registration.'},
                        status=status.HTTP_200_OK)
                    # return JsonResponse({'Status': True},
                    #                     status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse(
                        {'Status': False,
                         'Errors': user_serializer.errors},
                    )

        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST)


class UserEmailVerify(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id = get_object_or_404(Token.objects.all(), key=token).user_id
        user = get_object_or_404(User.objects.all(), pk=user_id)

        serializer = UserSerializer(instance=user,
                                    data={'email_is_verified': True,
                                          'is_active': True},
                                    partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'User': user.email,
                             'Message': 'Yor registration is confirmed.'},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class EditUser(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User.objects.all(), pk=self.request.user.id)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User.objects.all(), pk=self.request.user.id)
        user_data = self.request.data

        serializer = UserSerializer(instance=user, data=user_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ConfirmAccount(APIView):
    """
    Подтверждение регистрации
    """
    permission_classes = [AllowAny]

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data['email'], is_active=True)
        if user:
            return JsonResponse(
                {'Message': _('Confirmation has been done earlier')},
                status=status.HTTP_200_OK)

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                # reset_password_token_created.send(sender=self.__class__,
                # user_id=user.id)
                token.delete()
                return JsonResponse(
                    {'Message': _('Registration complete successfully')},
                    status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {'Errors': _('Неправильно указан токен или email')},
                    status=status.HTTP_403_FORBIDDEN)

        return JsonResponse({'Errors': 'Не указаны все необходимые аргументы'},
                            status=status.HTTP_411_LENGTH_REQUIRED)


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

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

        serializer = ContactSerializer(data=contact_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        items_list = request.data.get('items').split(',')
        deleted_items = 0

        for item in items_list:
            super().get_queryset().filter(pk=item).delete()
            deleted_items += 1

        return Response({'message': f'Deleted {deleted_items} otems.'},
                        status=status.HTTP_200_OK)
