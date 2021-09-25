from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bank_code = models.CharField(max_length=255, null=True)
    bank_account_number = models.CharField(max_length=255, null=True)
    bank_account_name = models.CharField(max_length=255, null=True)

    # is set to True when bank account information is verified
    is_verified = models.BooleanField(default=False)
