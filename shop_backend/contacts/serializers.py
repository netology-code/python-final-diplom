from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserInfo
from rest_framework.exceptions import ValidationError


class UserRegisterSerializer(serializers.ModelSerializer):
    middle_name = serializers.CharField(max_length=50, write_only=True)
    company = serializers.CharField(max_length=50, write_only=True)
    position = serializers.CharField(max_length=50, write_only=True)
    password_repeat = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'password', 'password_repeat', 'company',
                  'position']

    def create(self, validated_data):
        new_user, is_new_user_created = User.objects.get_or_create(
            email=validated_data.get('email'),
            defaults={
                'first_name': validated_data.get('first_name'),
                'last_name': validated_data.get('last_name'),
                'username': validated_data.get('email'),
                'password': validated_data.get('password'),
            }
        )

        if not is_new_user_created:
            raise ValidationError({'email': ['User with this email already exists.']})

        new_user_info = UserInfo(
            user_id=new_user.id,
            middle_name=validated_data.get('middle_name'),
            company=validated_data.get('company'),
            position=validated_data.get('position')
        )
        new_user_info.save()

        return validated_data

    def validate(self, data):
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError({'password': ['Passwords are different.']})

        return data
