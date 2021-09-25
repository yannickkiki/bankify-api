from django.conf import settings

from paystackapi.paystack import Paystack


class PaystackAPI:

    def __init__(self):
        self.client = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)

    def verify_account(self, account_number, bank_code):
        if settings.DEBUG is False:
            return self.client.verification.verify_account(
                account_number=account_number, bank_code=bank_code
            )
        else:
            if (account_number, bank_code) == ("account-number-test", "bank-code-test"):
                return {
                    "status": True,
                    "message": "Account number resolved",
                    "data": {
                        "account_number": "account-number-test",
                        "account_name": "John DOE"
                    }
                }
            raise NotImplementedError(
                "We only accept account_number:'account-number-test' and "
                "bank_code: 'bank-code-test' in DEBUG mode"
            )


paystack_api = PaystackAPI()
