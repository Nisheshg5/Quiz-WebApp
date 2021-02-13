from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Textarea, TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.formats import base_formats

from .forms import SignUpForm
from .models import Account, Question, Question_bank, Quiz, QuizTakers, Response


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


class QuizAdmin(admin.ModelAdmin):
    class QuestionAdmin(admin.TabularInline):
        model = Question
        formfield_overrides = {
            models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 20})},
        }

        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(QuizAdmin.QuestionAdmin, self).formfield_for_dbfield(
                db_field, **kwargs
            )
            if db_field.name == "question":
                field.widget.attrs["cols"] = 40
            return field

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
    inlines = [
        QuestionAdmin,
    ]
    change_form_template = "quiz_app/admin_quiz_change_form.html"


class Question_bank_admin(ImportExportModelAdmin):
    class Question_bank_resource(resources.ModelResource):
        id = Field(attribute="id")
        question = Field(attribute="question", column_name="Question Statement")
        choice_1 = Field(attribute="choice_1", column_name="Option 1")
        choice_2 = Field(attribute="choice_2", column_name="Option 2")
        choice_3 = Field(attribute="choice_3", column_name="Option 3")
        choice_4 = Field(attribute="choice_4", column_name="Option 4")
        choice_5 = Field(attribute="choice_5", column_name="Option 5")
        correct = Field(attribute="correct", column_name="Correct Answer-1")
        marks = Field(attribute="marks", column_name="Marks", default=1)
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

    def get_import_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_import()]

    def add_questions_to_quiz(self, request, queryset):
        quiz_id = request.GET.get("quizid", "")
        if not quiz_id:
            messages.error(
                request, mark_safe("No Quiz Entered<br>Please Select A Quiz First")
            )
            return redirect(request.get_full_path())

        try:
            quiz = Quiz.objects.filter(pk=quiz_id).first()
        except ValidationError:
            messages.error(request, mark_safe("Invalid Quiz Id Found"))
            return redirect(request.get_full_path())

        if not quiz:
            messages.error(request, mark_safe("No Quiz Found For Given ID"))
            return redirect(request.get_full_path())

        if "apply" in request.POST:
            if request.POST.get("apply", "") == "Cancel":
                return redirect(request.get_full_path())

            print(self, request, quiz, *queryset, sep="\n")
            return redirect(request.get_full_path())

        context = {
            "question_bank": queryset,
            "quiz": quiz,
        }
        return render(
            request, "quiz_app/admin_question_bank_confirmation.html", context=context
        )

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
    actions = ["add_questions_to_quiz"]
    resource_class = Question_bank_resource


class QuizTakersAdmin(admin.ModelAdmin):
    class ResponseAdmin(admin.TabularInline):
        model = Response

    list_display = (
        "quiz",
        "user",
        "completed",
        "started",
    )

    search_fields = (
        "quiz",
        "user",
    )
    list_filter = (
        "quiz",
        "user",
    )
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question_bank, Question_bank_admin)
admin.site.register(QuizTakers, QuizTakersAdmin)
