from globals.serializers import DynamicFieldsModelSerializer
from .models import User


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('is_superuser', 'is_staff', 'is_active',
                            'groups', 'user_permissions', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}
