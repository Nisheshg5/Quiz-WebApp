import json
import random
from json import JSONEncoder
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import datetime
from django.views import generic

from .forms import QuizForm, QuizPasswordForm, SignUpForm
from .models import Question, Quiz, QuizTakers, Response

old_default = JSONEncoder.default


def new_default(self, obj):
    if isinstance(obj, UUID):
        return str(obj)
    return old_default(self, obj)


JSONEncoder.default = new_default


def home(request):
    quiz_id = request.GET.get("quiz_id")
    if quiz_id:
        try:
            val = UUID(quiz_id).version
            if val != 4:
                raise ValueError(0)
            quiz = Quiz.objects.filter(pk=quiz_id).first()
            if quiz:
                if not quiz.has_started:
                    return redirect("quiz_upcoming", quiz_id=quiz_id)
                elif not quiz.has_ended:
                    return redirect("quiz_started", quiz_id=quiz_id)
                else:
                    return redirect("quiz_ended", quiz_id=quiz_id)

            else:
                messages.error(request, "No Quiz Found For Given ID")
                return redirect("home")

        except ValueError:
            messages.error(request, "Invalid Id")
            return redirect("home")

    quizForm = QuizForm()
    context = {"quizForm": quizForm}
    return render(request, "quiz_app/home.html", context)


def quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    quizTaker = QuizTakers.objects.filter(quiz=quiz, user=request.user)
    questions = []

    if quizTaker.exists():
        quizTaker = quizTaker.first()
        queryset = quizTaker.response_set.all()

        for response in queryset:
            questions.append(model_to_dict(response.question, exclude=["correct"]))
    else:
        quizTaker = QuizTakers.objects.create(quiz=quiz, user=request.user)
        shuffledQuestions = quiz.question_set.all()[::1]
        random.shuffle(shuffledQuestions)

        for question in shuffledQuestions:
            response = Response(quiztaker=quizTaker, question=question)
            response.save()
            questions.append(model_to_dict(question, exclude=["correct"]))

    shuffle = quiz.isShuffle
    context = {
        "quiz": quiz,
        "questions": json.dumps(questions),
        "shuffle": json.dumps(shuffle),
        "quizTaker": quizTaker,
    }
    return render(request, "quiz_app/quiz.html", context)


def saveResponse(request):
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        answer = request.POST.get("answer")
        print(request.POST)
        print(quizTaker)
        print(answer)

    return HttpResponse("{}", content_type="application/json")


# quiz results route
# @/quiz/<quiz_id>/result
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    # fetch from the database
    # quiz questions, user answers, correct answers

    context = {}
    return render(request, "quiz_app/quiz_result.html", context)


def quiz_upcoming(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)
    if quiz.has_started:
        return redirect("quiz_started", quiz_id=quiz_id)

    form = QuizPasswordForm(request.POST or None)
    context = {"quiz": quiz, "form": form}
    return render(request, "quiz_app/quiz_upcoming.html", context)


def quiz_started(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)

    form = QuizPasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and Quiz.objects.filter(
            pk=quiz_id, password=request.POST.get("password")
        ):
            return redirect("quiz_instructions", quiz_id=quiz_id)
        else:
            messages.error(request, "Wrong Password")

    context = {"quiz": quiz, "form": form}
    return render(request, "quiz_app/quiz_started.html", context)


def quiz_ended(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if not quiz.has_ended:
        return redirect("quiz_started", quiz_id=quiz_id)

    form = QuizPasswordForm(request.POST or None)
    context = {"quiz": quiz, "form": form}
    return render(request, "quiz_app/quiz_ended.html", context)


def quiz_instructions(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz_instructions.html", context)


def about(request):
    return render(request, "quiz_app/about.html")


def contact(request):
    return render(request, "quiz_app/contact.html")


def hello_there(request, name):
    return render(
        request, "quiz_app/hello_there.html", {"name": name, "date": datetime.now()}
    )


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


# def hello_there(request, name):
#     now = datetime.now()
#     formatted_now = now.strftime("%A, %d %B, %Y at %X")

#     # Filter the name argument to letters only using regular expressions. URL arguments
#     # can contain arbitrary text, so we restrict to safe characters only.
#     match_object = re.match("[a-zA-Z]+", name)

#     if match_object:
#         clean_name = match_object.group(0)
#     else:
#         clean_name = "Friend"

#     content = "Hello there, " + clean_name + "! It's " + formatted_now
#     return HttpResponse(content)
