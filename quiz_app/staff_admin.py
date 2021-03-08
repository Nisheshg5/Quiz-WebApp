import json
from collections import Counter

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db import models
from django.db.models import Sum
from django.forms import Textarea
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import ugettext_lazy as _

from .forms import QuizAddFormStaff
from .models import Account, Question, Question_bank, Quiz, QuizTakers, Response


class StaffAdminSite(AdminSite):
    def home(*args):
        return HttpResponseRedirect(reverse("staff_admin:quiz_app_quiz_changelist"))

    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


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
        return TemplateResponse(request, "admin/quiz_report.html", context)

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
    change_form_template = "admin/quiz_change_form.html"


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.enable_nav_sidebar = False

staff_admin_site.register(Quiz, QuizAdmin)
