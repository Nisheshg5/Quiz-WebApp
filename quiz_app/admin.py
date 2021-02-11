from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import SignUpForm
from .models import Account, Question_bank, Quiz


class AccountAdmin(UserAdmin):
    add_form = SignUpForm

    list_display = (
        "full_name",
        "email",
        "date_joined",
        "last_login",
        "is_admin",
        "is_staff",
    )
    search_fields = (
        "full_name",
        "email",
    )
    ordering = (
        "full_name",
        "email",
    )

    readonly_fields = ("id", "date_joined", "last_login")

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class QuestionBankAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "choice_1",
        "choice_2",
        "choice_3",
        "choice_4",
        "choice_5",
        "correct",
        "isShuffle",
        "tag",
        "level",
    )
    search_fields = ("question",)
    list_filter = (
        "tag",
        "level",
    )
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Quiz)
admin.site.register(Question_bank, QuestionBankAdmin)
