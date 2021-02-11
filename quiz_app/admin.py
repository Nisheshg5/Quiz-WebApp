from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

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


class Question_bank_resource(resources.ModelResource):
    id = Field(attribute="id")
    question = Field(attribute="question", column_name="Question Statement")
    choice_1 = Field(attribute="choice_1", column_name="Option 1")
    choice_2 = Field(attribute="choice_2", column_name="Option 2")
    choice_3 = Field(attribute="choice_3", column_name="Option 3")
    choice_4 = Field(attribute="choice_4", column_name="Option 4")
    choice_5 = Field(attribute="choice_5", column_name="Option 5")
    correct = Field(attribute="correct", column_name="Correct Answer-1")
    tag = Field(attribute="tag", column_name="Tag")
    isShuffle = Field(attribute="isShuffle", column_name="isShuffle")
    level = Field(attribute="level", column_name="Level", default="easy")

    class Meta:
        model = Question_bank


class Question_bank_admin(ImportExportModelAdmin):
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
    resource_class = Question_bank_resource


admin.site.register(Account, AccountAdmin)
admin.site.register(Quiz)
admin.site.register(Question_bank, Question_bank_admin)
