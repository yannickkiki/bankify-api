import graphene

from .retrieve_account_name import RetrieveAccountNameMixin


class Query(RetrieveAccountNameMixin, graphene.ObjectType):
    pass
