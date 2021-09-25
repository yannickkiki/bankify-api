Bankify is a GraphQL API that lets you enter and retrieve your bank info. For 
the bank info entry, a validation of the information is done with the account 
number resolution API of PayStack.

Quick start
-----------
1. Create Virtualenv with python3.9 (the code should also work with 3.6, 3.7, 3.8 
currently):

```shell
    virtualenv venv --python=python3.9
```

2. Activate virtual env:

```shell
    source venv/bin/activate
```

3. Install the requirements:

```shell
   pip install -r requirements.txt
```

4. Run database migrations (SQLite database with the current conf):

```shell
   python manage.py migrate
```

5. Run the dev server:

```shell
   python manage.py runserver 127.0.0.1:8000
```

Features
-----------
### Set user bank info (cf. bankify/user/schema/mutation/set_user_bank_info.py):

This a mutation that takes as parameters `user_account_number`,
`user_bank_code`, and `user_account_name`; makes a request on
paystack API to verify that the `user_account_name` matches with PayStack 
records ("matched" here means that the Levenshtein distance is <=2) and if good,
store the bank info and sets the user as verified.

To test this, you can generate an authentication token for one of the user populated 
in the database (username: bankify, password: bankify, cf. user/migrations/0002) 
and make the mutation to set the bank info:

#### Generate the token

```shell
    curl --request POST \
      --url http://localhost:8000/graphql/ \
      --header 'content-type: application/json' \
      --data '{"query":"mutation {\n  tokenAuth (\n    username: \"bankify\",\n    password: \"bankify\"\n  )\n  {\n    token\n  }\n}\n"}'
```

#### Set bank info

```shell
    curl --request POST \
      --url http://localhost:8000/graphql/ \
      --header 'authorization: JWT auth-token' \
      --header 'content-type: application/json' \
      --data '{"query":"mutation {\n  setUserBankInfo(userAccountNumber:\"account-number-test\", userBankCode:\"bank-code-test\", userAccountName: \"John Doe\") {\n    user{\n      isVerified\n    }\n  }\n}"}'
```

* Make sure to replace `auth-token` by the token you got from the previous request.
* Tokens expire in 5 minutes (cf. config/settings.py->GRAPHQL_JWT)

You should get `user{isVerified:true}` as result.

To test with real data, you will need to set DEBUG=False in the settings
(config/settings.py) because in DEBUG mode, we simulate the paystack API 
and return account_name:"John DOE" (cf. xlib/paystack.py->PaystackAPI), that's why the
user in the mutation above have been successfully verified with these entries.
You will also need to set your paystack secret key in the settings(PAYSTACK_SECRET_KEY)

To confirm that the Levenshtein distance check is working, you can make the 
previous request with an account_name that have distance 1 or 2 with "John Doe".
Example : "Joan Do", distance:2.
You should also get `user{isVerified:true}` as result.

After that, you can test with "Dummy Name" to confirm that the validation fails when
the account name does not match.

PS: The automated tests are in bankify/user/tests/test_schema.py
To run the tests:
```shell
    python manage.py test --debug-mode
```

### Retrieve account name (cf bankify/user/schema/query/retrieve_account_name.py)
#### From db if exists
Here, since the account_name returned by paystack api is "John Doe", we might want to
set the name in database to something different to ensure the result we will get actually
come from the db. So you can get a new token with username:bankify, password:bankify (in 
case the previous token is already expired), set bank info with account_name: "Joan Do"
and then make the query to retrieve account name:
```shell
curl --request POST \
  --url http://localhost:8000/graphql/ \
  --header 'authorization: JWT auth-token' \
  --header 'content-type: application/json' \
  --data '{"query":"query {\n  accountName(bankCode: \"bank-code-test\", accountNumber:\"account-number-test\")\n}\n"}'
```
This should return `{"accountName":"Joan Do"}`

#### From paystack since not existing in db
To ensure the account name does not exist in the db, we can test with the other user 
populated in the database, so you can generate a token for username:bankai,password:bankai
and make the query to retrieve account with the token obtained. You should get 
`{"accountName":"John DOE"}` as this is the account name returned by
the paystack api.


* What's a good reason why the pure Levenshtein Distance algorithm might be a more 
effective solution than the broader Damerau–Levenshtein Distance algorithm in this 
specific scenario ?

The Damerau-Levenshtein algorithm adds the possibility of making a transposition between 
two successive characters, so for certain pairs of strings, the distance given by the 
Damerau-Levenshtein algorithm will be smaller than the one given by Levenshtein.

Example: make, mkae; Distance Levenshtein: 2, Distance Damerau-Levenshtein: 1

This implies in our case that the Damerau-Levenshtein algorithm will validate 
more account names than the Levenshtein algorithm, which can be interesting for error 
correction but could also validate more false positives and this could be annoying.

So, the Levenshtein might be more interesting in the sense that it will have a lower wrong 
validation rate.
