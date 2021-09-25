from graphene_django import DjangoObjectType

from bankify.user.models import User


class UserType(DjangoObjectType):

    class Meta:
        model = User
