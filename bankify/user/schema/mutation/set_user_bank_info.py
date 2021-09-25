import graphene

from graphql_jwt.decorators import login_required
from Levenshtein import distance as levenshtein_distance

from bankify.xlib import paystack_api
from bankify.user.schema.type import UserType


class SetUserBankInfo(graphene.Mutation):
    class Arguments:
        user_account_number = graphene.String(required=True)
        user_bank_code = graphene.String(required=True)
        user_account_name = graphene.String(required=True)

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, user_account_number, user_bank_code, user_account_name):
        result = paystack_api.verify_account(
            account_number=user_account_number, bank_code=user_bank_code
        )
        assert result["status"] is True, \
            "Unable to verify your bank account information. Check if your entries " \
            "are correct, please."

        account_name_paystack = result["data"]["account_name"].upper()
        account_name_argument = user_account_name.upper()
        assert levenshtein_distance(account_name_paystack, account_name_argument) <= 2, \
            "The account name you entered does not correspond to the account number."

        user = info.context.user
        user.bank_account_number = user_account_number
        user.bank_code = user_bank_code
        user.bank_account_name = user_account_name
        user.is_verified = True
        user.save()
        return SetUserBankInfo(user)
