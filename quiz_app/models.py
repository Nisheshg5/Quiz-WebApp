from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")

        user = self.model(email=self.normalize_email(email), username=username,)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=self.normalize_email(email), username=username, password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=254, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = "account"



class Quiz(models.Model):
    def default_start_datetime():
        return datetime.utcnow() + timedelta(hours=3)

    def default_end_datetime():
        return datetime.utcnow() + timedelta(hours=6)

    quiz_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=30, blank=False, null=False)
    instructions = models.TextField(default="Instructions here")
    password = models.CharField(max_length=120)
    start_date = models.DateTimeField(
        verbose_name="start time", default=default_start_datetime
    )
    end_date = models.DateTimeField(
        verbose_name="end time", default=default_end_datetime
    )
    duration = models.IntegerField(default=90)

    def __str__(self):
        return f"id: {self.quiz_id}, title: {self.title}"

    class Meta:
        db_table = "quiz"
        app_label = "quiz_app"
