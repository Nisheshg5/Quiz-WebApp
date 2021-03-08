from django.contrib.admin import AdminSite
from .models import Account, Question, Question_bank, Quiz, QuizTakers, Response
from django.urls import reverse
from django.http import HttpResponseRedirect


class StaffAdminSite(AdminSite):
    def home(*args):
        return HttpResponseRedirect(reverse("staff_admin:quiz_app_quiz_changelist"))

    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.enable_nav_sidebar = False

staff_admin_site.register(Quiz)
