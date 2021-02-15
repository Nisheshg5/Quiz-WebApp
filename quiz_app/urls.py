from django.urls import path

from quiz_app import views

from .views import SignUpView

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/<quiz_id>", views.quiz, name="quiz"),
    path("quiz/<quiz_id>/result", views.quiz_result, name="quiz_result"),
    path("quiz/upcoming/<quiz_id>", views.quiz_upcoming, name="quiz_upcoming"),
    path("quiz/started/<quiz_id>", views.quiz_started, name="quiz_started"),
    path("quiz/ended/<quiz_id>", views.quiz_ended, name="quiz_ended"),
    path("quiz/instructions/<quiz_id>", views.quiz_instructions, name="quiz_instructions"),
    path("quiz/response/save/", views.saveResponse, name="save_response"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("signup/", SignUpView.as_view(), name="signup"),
]
