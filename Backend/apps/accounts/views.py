from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import CustomUserSerializer
from .models import CustomUser as User

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
