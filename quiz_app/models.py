import random
import string
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from smtplib import SMTPException
from uuid import uuid4

import pytz
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, EmailMultiAlternatives, send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from verify_email.app_configurations import GetFieldFromSettings
from verify_email.email_handler import _VerifyEmail


class AccountManager(BaseUserManager):
    def create_user(self, email, full_name, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not full_name:
            raise ValueError("User must provid a name")

        user = self.model(email=self.normalize_email(email), full_name=full_name,)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
        user = self.create_user(
            email=self.normalize_email(email), full_name=full_name, password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    full_name = models.CharField(max_length=30, unique=False)
    email = models.EmailField(verbose_name="email", max_length=254, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    timeZone = models.CharField(
        max_length=30,
        default="Asia/Kolkata",
        choices=[(tz, tz) for tz in pytz.common_timezones],
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "full_name",
    ]

    objects = AccountManager()

    def __str__(self):
        return f"{self.full_name}\t\t{self.email}"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    class VerifyEmail(_VerifyEmail):
        def send_verification_link(self, request, user):
            try:
                useremail = user.email
                verification_url = self.__make_verification_url(
                    request, user, useremail
                )
                subject = self.settings.get("subject")
                msg = render_to_string(
                    self.settings.get("html_message_template", raise_exception=True),
                    {"link": verification_url},
                )

                try:
                    send_mail(
                        subject,
                        strip_tags(msg),
                        from_email=self.settings.get("from_alias"),
                        recipient_list=[useremail],
                        html_message=msg,
                    )
                    return user
                except (BadHeaderError, SMTPException):
                    # user.delete()
                    return False

            except Exception as error:
                # user.delete()
                if self.settings.get("debug_settings"):
                    raise Exception(error)

    def verify_email(self, request):
        return Account.VerifyEmail().send_verification_link(request, self)

    class Meta:
        db_table = "account"


class Quiz(models.Model):
    def default_start_datetime():
        return datetime.utcnow() + timedelta(hours=3)

    def default_end_datetime():
        return datetime.utcnow() + timedelta(hours=6)

    def random_code():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def save(self, *args, **kwargs):
        self.key = self.key.upper()
        return super(Quiz, self).save(*args, **kwargs)

    quiz_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=30, blank=False, null=False)
    instructions = models.TextField(default="Instructions here")
    description = models.TextField(default="Description here")
    key = models.CharField(
        unique=True,
        max_length=8,
        validators=[MinLengthValidator(6)],
        default=random_code,
    )
    extra = models.TextField(default="Roll No")
    start_date = models.DateTimeField(
        verbose_name="start time", default=default_start_datetime
    )
    end_date = models.DateTimeField(
        verbose_name="end time", default=default_end_datetime
    )
    duration = models.IntegerField(default=90)
    isShuffle = models.BooleanField(default=True)
    allow_backtracking = models.BooleanField(default=True)
    isProctored = models.BooleanField(default=True)
    showResults = models.BooleanField(default=True)
    max_suspicion_count = models.IntegerField(default=999)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.quiz_id}, title: {self.title}"

    @property
    def has_started(self):
        return self.start_date < timezone.now()

    @property
    def has_ended(self):
        return self.end_date < timezone.now()

    @property
    def time_till_starts(self):
        return (self.start_date - timezone.now()).total_seconds()

    class Meta:
        db_table = "quiz"
        app_label = "quiz_app"
        verbose_name_plural = "Quizzes"
        ordering = [
            "created_at",
        ]


class Question_bank(models.Model):

    C = "C"
    CPLUSPLUS = "C++"
    JAVA = "java"
    PYTHON = "python"
    OS = "os"
    CSA = "csa"
    DS = "ds"
    TAGS = [
        (C, "C"),
        (CPLUSPLUS, "C++"),
        (JAVA, "Java"),
        (PYTHON, "Python"),
        (OS, "OS"),
        (CSA, "CSA"),
        (DS, "DS"),
    ]

    BEGINNER = "easy"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    LEVELS = [
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    ]

    title = models.TextField()
    choice_1 = models.TextField()
    choice_2 = models.TextField()
    choice_3 = models.TextField(blank=True, null=True)
    choice_4 = models.TextField(blank=True, null=True)
    choice_5 = models.TextField(blank=True, null=True)
    correct = models.TextField()
    marks = models.IntegerField(default=1)
    tag = models.CharField(max_length=10, choices=TAGS)
    isShuffle = models.BooleanField(default=True)
    level = models.CharField(max_length=15, choices=LEVELS, default=BEGINNER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "question_bank"
        app_label = "quiz_app"
        verbose_name_plural = "question_bank"
        ordering = [
            "created_at",
            "tag",
            "level",
        ]


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    title = models.TextField()
    choice_1 = models.TextField()
    choice_2 = models.TextField()
    choice_3 = models.TextField(blank=True, null=True)
    choice_4 = models.TextField(blank=True, null=True)
    choice_5 = models.TextField(blank=True, null=True)
    correct = models.TextField()
    marks = models.IntegerField(default=1)
    isShuffle = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "question"
        app_label = "quiz_app"
        verbose_name_plural = "questions"
        ordering = [
            "marks",
            "created_at",
        ]

    def __str__(self):
        return f"Question id: {self.pk}"


class QuizTakers(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    extra = models.TextField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)
    suspicion_count = models.IntegerField(default=0)

    @property
    def time_remaining(self):
        return (
            self.started + timedelta(minutes=self.quiz.duration) - timezone.now()
        ).total_seconds()

    @property
    def has_ended(self):
        if self.completed:
            return True
        time = self.started + timedelta(minutes=self.quiz.duration) - timezone.now()
        if time.total_seconds() <= 0:
            self.completed = self.started + timedelta(minutes=self.quiz.duration)
        return time.total_seconds() <= 0

    class Meta:
        db_table = "QuizTaker"
        app_label = "quiz_app"
        verbose_name_plural = "QuizTakers"
        constraints = [
            models.UniqueConstraint(fields=["quiz", "user"], name="Unique Quiz Taker"),
        ]
        ordering = [
            "quiz",
            "user",
        ]


class Response(models.Model):
    quiztaker = models.ForeignKey(QuizTakers, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)
    isCorrect = models.BooleanField(default=False)
    marks = models.IntegerField(default=0)

    class Meta:
        db_table = "response"
        app_label = "quiz_app"
        verbose_name_plural = "responses"
        constraints = [
            models.UniqueConstraint(
                fields=["quiztaker", "question"], name="Unique Response"
            ),
        ]
        ordering = [
            "quiztaker",
            "question",
        ]
