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

from .admin import AccountAdmin, Question_bank_admin, QuestionAdmin, QuizAdmin
from .forms import QuizAddForm, QuizAddFormStaff, SignUpForm
from .models import Account, Question, Question_bank, Quiz, QuizTakers


class StaffAdminSite(AdminSite):
    def home(*args, **kwargs):
        return HttpResponseRedirect(reverse("staff_admin:quiz_app_quiz_changelist"))

    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


class AccountAdmin(AccountAdmin):
    def __init__(self, *args, **kwargs):
        super(AccountAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class QuestionAdmin(QuestionAdmin):
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class QuizAdmin(QuizAdmin):
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

    def save_model(self, request, obj, form, change):
        if not change and not obj.invigilator:
            obj.invigilator = request.user
        super(QuizAdmin, self).save_model(request, obj, form, change)

    inlines = [
        QuestionAdmin,
    ]


class Question_bank_admin(Question_bank_admin):
    def __init__(self, *args, **kwargs):
        super(Question_bank_admin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and obj and obj.invigilator == request.user

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.register(Account, AccountAdmin)
staff_admin_site.register(Quiz, QuizAdmin)
staff_admin_site.register(Question_bank, Question_bank_admin)
