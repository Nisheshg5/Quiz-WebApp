from django.urls import path

from quiz_app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/<quiz_id>", views.quiz, name="quiz"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
