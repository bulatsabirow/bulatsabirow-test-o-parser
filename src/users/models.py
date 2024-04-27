from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.IntegerField(unique=True)

    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ["telegram_id"]
