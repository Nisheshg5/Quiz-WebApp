from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


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
    isShuffle = models.BooleanField(default=True)
    allow_backtracking = models.BooleanField(default=True)
    isProctered = models.BooleanField(default=True)
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
