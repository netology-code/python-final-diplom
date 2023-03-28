# from pprint import pprint

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
# from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from orders.send_email import send_email_4_verification
from orders.serializers import UserSerializer, ContactSerializer
from orders.models import User, ConfirmEmailToken, Contact
from orders.permissions import IsOwner
from django_rest_passwordreset.serializers import EmailSerializer
from django_rest_passwordreset.signals import pre_password_reset, post_password_reset
from django_rest_passwordreset.models import ResetPasswordToken, \
    clear_expired, get_password_reset_token_expiry_time, \
    get_password_reset_lookup_field
from django_rest_passwordreset.views import _unicode_ci_compare, \
    HTTP_USER_AGENT_HEADER, HTTP_IP_ADDRESS_HEADER
from django.utils import timezone
from datetime import timedelta
from rest_framework import exceptions
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import get_password_validators
from django.conf import settings
from orders.send_email import send_email_4_reset_passw


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
                token.user.email_is_verified = True
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


class UserEmailVerify(APIView):
    """
    Подтверждение регистрации
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

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


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        This view should return CRUD of all the contacts
        for the currently authenticated user.
        """
        print('get_queryset')
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


class ResetPasswordRequestToken(GenericAPIView):
    """
    An Api View which provides a method to request a
    password reset token based on an e-mail address

    Sends a signal reset_password_token_created when a
    reset token was created
    """
    throttle_classes = ()
    permission_classes = ()
    serializer_class = EmailSerializer
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # before we continue, delete all existing expired tokens
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # datetime.now minus expiry hours
        now_minus_expiry_time = timezone.now() - timedelta(
            hours=password_reset_token_validation_time)

        # delete all tokens where created_at < now - 24 hours
        clear_expired(now_minus_expiry_time)

        # find a user by email address (case insensitive search)
        users = User.objects.filter(
            **{'{}__iexact'.format(get_password_reset_lookup_field()): email})

        active_user_found = False

        # iterate over all users and check if there is any user that is active
        # also check whether the password can be changed (is useable),
        # as there could be users that are not allowed
        # to change their password (e.g., LDAP user)
        for user in users:
            if user.eligible_for_reset():
                active_user_found = True
                break

        # No active user found, raise a validation error
        # but not if DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE == True
        if not active_user_found and not getattr(
                settings,
                'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE',
                False):
            raise exceptions.ValidationError({
                'email':
                    [_(
                        "We couldn't find an account associated with that email.")],
            })

        # last but not least: iterate over all users that
        # are active and can change their password
        # and create a Reset Password Token and send a signal with the created token
        for user in users:
            if user.eligible_for_reset() and \
                    _unicode_ci_compare(email,
                                        getattr(user,
                                                get_password_reset_lookup_field())):
                # define the token as none for now
                token = None

                # check if the user already has a token
                if user.password_reset_tokens.all().count() > 0:
                    # yes, already has a token, re-use this token
                    token = user.password_reset_tokens.all()[0]
                else:
                    # no token exists, generate a new token
                    token = ResetPasswordToken.objects.create(
                        user=user,
                        user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ''),
                        ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ''),
                    )
                # send a signal that the password token was created
                # let whoever receives this signal handle sending
                # the email for the password reset
                send_email_4_reset_passw(user, token)
        # done
        return Response({'status': 'OK',
                         'Message': 'Check your email..'},
                        status=status.HTTP_200_OK)


class ResetPasswordConfirm(GenericAPIView):
    """
    An Api View which provides a method to reset a password based on a unique token
    """

    def post(self, request, *args, **kwargs):

        password = request.data['password']
        token = request.data['token']

        # find token
        reset_password_token = Token.objects.filter(key=token).first()

        # change users password (if we got to this code it means that the user is_active)
        if reset_password_token.user.eligible_for_reset():
            pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)
            try:
                # validate the password against existing validators
                validate_password(
                    password,
                    user=reset_password_token.user,
                    password_validators=get_password_validators(
                        settings.AUTH_PASSWORD_VALIDATORS),
                )
            except ValidationError as e:
                # raise a validation error for the serializer
                raise exceptions.ValidationError({
                    'password': e.messages,
                })

            reset_password_token.user.set_password(password)
            reset_password_token.user.save()
            post_password_reset.send(sender=self.__class__,
                                     user=reset_password_token.user)

        # Delete all password reset tokens for this user
        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

        return Response({'status': 'OK',
                         'Message': 'Password was changed.'},
                        status=status.HTTP_200_OK)
