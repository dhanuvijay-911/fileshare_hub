from rest_framework import serializers
from .models import File
from users.models import UserProfile
from django.contrib.auth.models import User

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ShareFileSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserProfile
        fields = ['user', 'profile_picture']
