from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
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


class EmptyQuizIDFilter(SimpleListFilter):
    title = _("Empty Filter For Quiz")
    parameter_name = "quizid"

    def lookups(self, request, model_admin):
        return ()


class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "quiz_id",
        "title",
        "instructions",
        "password",
        "start_date",
        "end_date",
        "duration",
        "created",
    )

    readonly_fields = (
        "quiz_id",
        "created",
    )

    ordering = ("created",)

    change_form_template = "quiz_app/admin_quiz_change_form.html"


class Question_bank_admin(ImportExportModelAdmin):
    def add_questions_to_quiz(modeladmin, request, queryset):
        print(modeladmin, request, queryset)

    add_questions_to_quiz.short_description = "Add Questions To Quiz"

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
        EmptyQuizIDFilter,
    )
    lookup_fields = [
        "quiz_id",
    ]
    fieldsets = ()

    actions = [add_questions_to_quiz]
    resource_class = Question_bank_resource


admin.site.register(Account, AccountAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question_bank, Question_bank_admin)
