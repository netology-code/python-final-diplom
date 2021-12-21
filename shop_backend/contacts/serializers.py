from rest_framework import serializers
from .models import User
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password_repeat = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        new_user, _ = User.objects.get_or_create(
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

        return new_user

    def validate(self, data):
        password = data.get('password')
        password_repeat = data.get('password_repeat')
        if password != password_repeat:
            raise ValidationError({'password': ['Passwords are different.']})

        return data
