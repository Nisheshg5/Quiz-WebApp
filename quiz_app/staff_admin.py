from django.contrib.admin import AdminSite

from .models import Account, Question, Question_bank, Quiz, QuizTakers, Response


class EventAdminSite(AdminSite):
    site_header = "Staff Admin"
    site_title = "Staff Admin Portal"
    index_title = "Welcome"


event_admin_site = EventAdminSite(name="staff_admin")


event_admin_site.register(Quiz)
