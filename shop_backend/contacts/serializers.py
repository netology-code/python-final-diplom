from rest_framework import serializers
from .models import UserInfo
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class UserRegisterSerializer(serializers.ModelSerializer):
    middle_name = serializers.CharField(max_length=50)
    company = serializers.CharField(max_length=50)
    position = serializers.CharField(max_length=50)
    password_repeat = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'password', 'password_repeat', 'company',
                  'position']
        write_only_fields = ['middle_name', 'company', 'position']

    def create(self, validated_data):
        new_user, _ = User.objects.get_or_create(
            email=validated_data.get('email'),
            defaults={
                'first_name': validated_data.get('first_name'),
                'last_name': validated_data.get('last_name'),
                'password': validated_data.get('password'),
            }
        )

        new_user_info, _ = UserInfo.objects.update_or_create(
            user_id=new_user.id,
            defaults={
                'middle_name': validated_data.get('middle_name'),
                'company': validated_data.get('company'),
                'position': validated_data.get('position')
            }
        )

        return new_user

    def validate(self, data):
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError({'password': ['Passwords are different.']})

        return data
