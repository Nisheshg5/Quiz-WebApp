from django.urls import path

from quiz_app import ajax, views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/<quiz_id>", views.quiz, name="quiz"),
    path("quiz/result/<quiz_id>/", views.quiz_result, name="quiz_result"),
    path("quiz/export/<quiz_id>/", ajax.export_result, name="export_result"),
    path("quiz/upcoming/<quiz_id>", views.quiz_upcoming, name="quiz_upcoming"),
    path("quiz/started/<quiz_id>", views.quiz_started, name="quiz_started"),
    path("quiz/ended/<quiz_id>", views.quiz_ended, name="quiz_ended"),
    path("quiz/inst/<quiz_id>", views.quiz_instructions, name="quiz_instructions"),
    path("quiz/response/save/", ajax.saveResponse, name="save_response"),
    path("quiz/completed/", ajax.completed, name="completed"),
    path("signup/", views.signup, name="signup"),
]
