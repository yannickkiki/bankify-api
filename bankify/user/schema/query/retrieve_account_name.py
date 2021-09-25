import graphene
from graphql_jwt.decorators import login_required

from bankify.xlib import paystack_api


class RetrieveAccountNameMixin:
    account_name = graphene.String(
        bank_code=graphene.String(), account_number=graphene.String()
    )

    @login_required
    def resolve_account_name(self, info, bank_code, account_number):
        user = info.context.user
        if user.bank_account_name is not None:
            return user.bank_account_name

        result = paystack_api.verify_account(
            account_number=account_number, bank_code=bank_code
        )
        assert result["status"] is True, \
            "Unable to verify your bank account information. Check if your entries " \
            "are correct, please."

        account_name_paystack = result["data"]["account_name"]
        return account_name_paystack
