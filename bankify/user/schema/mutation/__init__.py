import graphene

from .set_user_bank_info import SetUserBankInfo


class Mutation(graphene.ObjectType):
    set_user_bank_info = SetUserBankInfo.Field()
