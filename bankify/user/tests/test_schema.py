from graphene_django.utils.testing import GraphQLTestCase

from bankify.user.models import User


class UserSchemaTest(GraphQLTestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="test", password="test")

    def setUp(self):
        self.auth_token = self._get_auth_token(username="test", password="test")

    def test_set_user_bank_info_correct(self):
        response = self._set_user_bank_info(
            user_account_number="account-number-test",
            user_bank_code="bank-code-test",
            user_account_name="John Doe"
        )
        self.assertTrue(response.json()["data"]["setUserBankInfo"]["user"]["isVerified"])

    def test_set_user_bank_info_correct_levenshtein(self):
        response = self._set_user_bank_info(
            user_account_number="account-number-test",
            user_bank_code="bank-code-test",
            user_account_name="Joan Do"
        )
        self.assertTrue(response.json()["data"]["setUserBankInfo"]["user"]["isVerified"])

    def test_set_user_bank_info_incorrect(self):
        response = self._set_user_bank_info(
            user_account_number="account-number-test",
            user_bank_code="bank-code-test",
            user_account_name="Dummy Name"
        )
        self.assertEqual(
            response.json()["errors"][0]["message"],
            "The account name you entered does not correspond to the account number."
        )

    def test_retrieve_account_name_db(self):
        self._set_user_bank_info(
            user_account_number="account-number-test",
            user_bank_code="bank-code-test",
            user_account_name="Joan Do"
        )

        response = self._retrieve_account_name(
            bank_code="bank-code-test",
            account_number="account-number-test"
        )
        self.assertEqual(response.json()["data"]["accountName"], "Joan Do")

    def test_retrieve_account_name_paystack(self):
        username, password = "testo", "testo"
        User.objects.create_user(username=username, password=password)
        self.auth_token = self._get_auth_token(username=username, password=password)

        response = self._retrieve_account_name(
            bank_code="bank-code-test",
            account_number="account-number-test"
        )
        self.assertEqual(response.json()["data"]["accountName"], "John DOE")

    def _get_auth_token(self, username, password):
        response = self.query(
            """
                mutation {
                    tokenAuth (
                        username: "%s",
                        password: "%s"
                    ){
                        token
                    }
                }
            """ % (username, password),
        )
        return response.json()["data"]["tokenAuth"]["token"]

    def _set_user_bank_info(self, user_account_number, user_bank_code, user_account_name):
        return self.query(
            """
                mutation {
                    setUserBankInfo(
                        userAccountNumber:"%s",
                        userBankCode:"%s",
                        userAccountName: "%s"
                    ){
                        user {
                            isVerified
                        }
                    }
                }
            """ % (user_account_number, user_bank_code, user_account_name),
            headers={"HTTP_AUTHORIZATION": f"JWT {self.auth_token}"}
        )

    def _retrieve_account_name(self, bank_code, account_number):
        return self.query(
            """
                query {
                    accountName(
                        bankCode: "%s",
                        accountNumber:"%s"
                    )
                }
            """ % (bank_code, account_number),
            headers={"HTTP_AUTHORIZATION": f"JWT {self.auth_token}"}
        )
