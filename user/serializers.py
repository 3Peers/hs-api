from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('is_superuser', 'is_staff', 'is_active',
                            'groups', 'user_permissions', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}