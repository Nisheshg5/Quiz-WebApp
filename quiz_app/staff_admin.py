import json
from collections import Counter

from django.contrib import admin, messages
from django.contrib.admin import AdminSite, SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, F, Sum
from django.forms import Textarea
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.formats import base_formats

from .forms import QuizAddForm, QuizAddFormStaff, SignUpForm
from .models import Account, Question, Question_bank, Quiz, QuizTakers, Response


class StaffAdminSite(AdminSite):
    def home(*args, **kwargs):
        return HttpResponseRedirect(reverse("staff_admin:quiz_app_quiz_changelist"))

    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


class AccountAdmin(UserAdmin):
    class EmptyQuizIDFilter(SimpleListFilter):
        title = _("Empty Filter For Quiz")
        parameter_name = "quizid"

        def lookups(self, request, model_admin):
            return ()

    def __init__(self, *args, **kwargs):
        super(AccountAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_action_choices(self, request):
        choices = super(AccountAdmin, self).get_action_choices(request)
        delete_choice = [(x, y) for x, y in choices if x == "delete_selected"]
        if delete_choice:
            del choices[choices.index(delete_choice[0])]
        choices.reverse()
        try:
            quiz_id = request.GET.get("quizid", None)
            if not quiz_id:
                raise Quiz.DoesNotExist()
            Quiz.objects.get(pk=quiz_id)
        except (Quiz.DoesNotExist, ValidationError):
            choices.pop(0)
        return choices

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def assign_users(self, request, queryset):
        quiz_id = request.GET.get("quizid", "")
        if not quiz_id:
            messages.error(
                request, mark_safe("No Quiz Entered<br>Please Select A Quiz First")
            )
            return redirect(request.get_full_path())

        try:
            quiz = Quiz.objects.prefetch_related(
                "quiztakers_set", "quiztakers_set__user"
            ).get(pk=quiz_id)
        except ValidationError:
            messages.error(request, mark_safe("Invalid Quiz Id Found"))
            return redirect(request.get_full_path())

        if not quiz:
            messages.error(request, mark_safe("No Quiz Found For Given ID"))
            return redirect(request.get_full_path())

        if "apply" in request.POST:
            if request.POST.get("apply", "") == "Cancel":
                return redirect(request.get_full_path())
            quizTakers = []
            for user in queryset:
                quizTaker = QuizTakers(quiz=quiz, user=user)
                quizTakers.append(quizTaker)
            QuizTakers.objects.bulk_create(quizTakers, ignore_conflicts=True)
            return redirect(request.get_full_path())

        context = {
            "quiz": quiz,
            "users": queryset,
        }
        return render(request, "staff_admin/user_confirmation.html", context=context)

    assign_users.short_description = "Assign Students To Test"

    add_form = SignUpForm

    list_display = (
        "full_name",
        "email",
        "date_joined",
        "last_login",
        "timeZone",
        "is_active",
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

    actions = ["assign_users"]
    filter_horizontal = ()
    list_filter = (EmptyQuizIDFilter,)
    fieldsets = (
        (None, {"fields": ("email", "password"),}),
        (_("Personal info"), {"fields": ("full_name", "timeZone")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser",),}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("full_name", "email", "password1", "password2"),
            },
        ),
    )


class QuizAdmin(admin.ModelAdmin):
    class QuestionAdmin(admin.TabularInline):
        model = Question
        question_numbering = 0
        fields = (
            "question_number",
            "quiz",
            "title",
            "choice_1",
            "choice_2",
            "choice_3",
            "choice_4",
            "choice_5",
            "correct",
            "marks",
            "isShuffle",
        )
        readonly_fields = ("question_number",)

        def question_number(self, obj):
            self.question_numbering += 1
            return f"{self.question_numbering:2}"

        question_number.short_description = "#"

        formfield_overrides = {
            models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 20})},
        }

        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(QuizAdmin.QuestionAdmin, self).formfield_for_dbfield(
                db_field, **kwargs
            )
            if db_field.name == "title":
                field.widget.attrs["cols"] = 40
            return field

        def has_view_permission(self, request, obj=None):
            return request.user.is_staff

        def has_add_permission(self, request):
            return request.user.is_staff

        def has_change_permission(self, request, obj=None):
            return request.user.is_staff

        def has_delete_permission(self, request, obj=None):
            return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and (
            (obj and obj.invigilator == request.user) or not obj
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(invigilator=request.user)

    def get_urls(self):
        urls = super(QuizAdmin, self).get_urls()
        my_urls = [
            path(
                "<quiz_id>/report/",
                self.admin_site.admin_view(self.quiz_report),
                name="quiz_report",
            ),
        ]
        return my_urls + urls

    def quiz_report(self, request, quiz_id):

        quiz = Quiz.objects.get(quiz_id=quiz_id)
        totalMarks = quiz.question_set.aggregate(Sum("marks"))["marks__sum"]
        marks = (
            QuizTakers.objects.filter(quiz=quiz)
            .prefetch_related("response_set__marks")
            .values_list("id")
            .annotate(marks_obtained=Sum("response__marks"))
        )
        marks = [i[1] for i in marks]
        marks = dict(Counter(marks))

        context = dict(
            self.admin_site.each_context(request),
            title="Report",
            quiz=quiz,
            marks=json.dumps(marks),
            totalMarks=totalMarks,
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            change=True,
            add=False,
            is_popup=False,
            save_as=False,
            has_delete_permission=False,
            has_add_permission=False,
            has_change_permission=True,
            has_view_permission=True,
            has_editable_inline_admin_formsets=True,
        )
        return TemplateResponse(request, "staff_admin/quiz_report.html", context)

    def get_action_choices(self, request):
        choices = super(QuizAdmin, self).get_action_choices(request)
        choices.pop(0)
        return choices

    def get_changeform_initial_data(self, request):
        get_data = super(QuizAdmin, self).get_changeform_initial_data(request)
        get_data["invigilator"] = request.user.pk
        return get_data

    list_display = (
        # "quiz_id",
        "title",
        "key",
        "extra",
        "start_date",
        "end_date",
        "duration",
        "isShuffle",
        "allow_backtracking",
        "isProctored",
        "max_suspicion_count",
        "created_at",
    )

    readonly_fields = (
        "quiz_id",
        "created_at",
    )

    ordering = ("-created_at",)
    inlines = [
        QuestionAdmin,
    ]
    form = QuizAddFormStaff
    change_form_template = "staff_admin/quiz_change_form.html"


class Question_bank_admin(ImportExportModelAdmin):
    class Question_bank_resource(resources.ModelResource):
        id = Field(attribute="id")
        title = Field(attribute="title", column_name="Question Statement")
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

    def __init__(self, *args, **kwargs):
        super(Question_bank_admin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def get_import_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_import()]

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and obj and obj.invigilator == request.user

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def get_action_choices(self, request):
        choices = super(Question_bank_admin, self).get_action_choices(request)
        choices.reverse()
        try:
            quiz_id = request.GET.get("quizid", None)
            if not quiz_id:
                raise Quiz.DoesNotExist()
            quiz = Quiz.objects.get(pk=quiz_id)
        except (Quiz.DoesNotExist, ValidationError):
            choices.pop(0)
        return choices

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

            questions = []
            for questionDict in queryset:
                question = Question(
                    quiz=quiz,
                    **model_to_dict(questionDict, exclude=["id", "tag", "level"]),
                )
                questions.append(question)
            Question.objects.bulk_create(questions)
            return redirect(request.get_full_path())

        context = {
            "question_bank": queryset,
            "quiz": quiz,
        }
        return render(
            request, "staff_admin/question_bank_confirmation.html", context=context
        )

    add_questions_to_quiz.short_description = "Add Questions To Quiz"

    list_display = (
        "title",
        "choice_1",
        "choice_2",
        "choice_3",
        "choice_4",
        "choice_5",
        "correct",
        "marks",
        "isShuffle",
        "tag",
        "level",
        "created_at",
    )

    search_fields = ("title",)
    list_filter = (
        "tag",
        "level",
        EmptyQuizIDFilter,
    )
    readonly_fields = ("created_at",)
    lookup_fields = [
        "quiz_id",
    ]
    fieldsets = ()
    actions = ["add_questions_to_quiz"]
    resource_class = Question_bank_resource
    change_list_template = "staff_admin/question_bank_list.html"


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.enable_nav_sidebar = False
staff_admin_site.register(Account, AccountAdmin)
staff_admin_site.register(Quiz, QuizAdmin)
staff_admin_site.register(Question_bank, Question_bank_admin)
