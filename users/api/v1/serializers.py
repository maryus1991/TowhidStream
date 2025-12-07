from users.models import User
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    model serializer for users
    """
    logo = Base64ImageField(represent_in_base64=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'logo',
            'link_of_stream',
            'description'
        ]