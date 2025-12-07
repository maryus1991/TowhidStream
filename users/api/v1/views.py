from rest_framework.generics import ListAPIView
from .serializers import UserSerializer
from users.models import User


class UserListAPIView(ListAPIView):
    """
    :return the of list all streams
    """

    serializer_class = UserSerializer


    def get_queryset(self):
        queryset = User.objects.filter(
            is_active=True, is_stream=True
        ).all()

        # todo: should be removed
        for item in queryset: item.get_link_of_stream()

        return queryset