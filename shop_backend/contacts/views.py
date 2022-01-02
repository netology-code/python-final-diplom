from rest_framework.viewsets import ModelViewSet
from contacts.models import User
from .serializers import UserRegisterSerializer
from rest_framework.permissions import IsAuthenticated


class UserRegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']
    # permission_classes = [IsAuthenticated]
