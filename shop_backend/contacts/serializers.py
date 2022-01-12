from rest_framework import serializers
from contacts.models import User
from django.db import transaction
from rest_framework.exceptions import ValidationError
from orders.models import Order


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'password', 'password_repeat', 'company',
                  'position']

    def create(self, validated_data):
        with transaction.atomic():
            new_user, is_new_user_created = User.objects.get_or_create(
                email=validated_data.get('email'),
                defaults={
                    'first_name': validated_data.get('first_name'),
                    'middle_name': validated_data.get('middle_name'),
                    'last_name': validated_data.get('last_name'),
                    'company': validated_data.get('company'),
                    'position': validated_data.get('position')
                }
            )

            if not is_new_user_created:
                raise ValidationError({'results': ['User with this email already exists.']})

            new_user.set_password(validated_data.get('password'))
            new_user.save()

            new_user_basket = Order(
                user=new_user
            )
            new_user_basket.save()

            return new_user

    def validate(self, data):
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError({'results': ['Passwords are different.']})

        return data
