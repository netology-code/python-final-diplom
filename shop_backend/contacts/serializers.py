from rest_framework import serializers
from contacts.models import User
from rest_framework.exceptions import ValidationError


class UserRegisterSerializer(serializers.ModelSerializer):
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
                'middle_name': validated_data.get('middle_name'),
                'last_name': validated_data.get('last_name'),
                'password': validated_data.get('password'),
                'company': validated_data.get('company'),
                'position': validated_data.get('position')
            }
        )

        if not is_new_user_created:
            raise ValidationError({'email': ['User with this email already exists.']})

        return new_user

    def validate(self, data):
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError({'password': ['Passwords are different.']})

        return data
