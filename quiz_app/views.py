import json
import random
from json import JSONEncoder
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import F
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import datetime
from django.views import generic
from verify_email.email_handler import send_verification_email

from quiz_app.excel import generate_result_as_excel

from .forms import QuizForm, QuizPasswordForm, SignUpForm
from .models import Account, Question, Quiz, QuizTakers, Response

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


context = {}


def quiz(request, quiz_id):
    global context
    if context:
        print("Fast Checkout")
        return render(request, "quiz_app/quiz.html", context)
    print("DB load")

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if not quiz.has_started:
        return redirect("quiz_upcoming", quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)

    try:
        quizTaker = QuizTakers.objects.get(quiz=quiz, user=request.user)
        if quizTaker.started and not quizTaker.completed:
            quizTaker.suspicion_count = F("suspicion_count") + 1
    except:
        pass

    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this.")
        return redirect("login")
    quizTaker = QuizTakers.objects.filter(quiz=quiz, user=request.user)
    if quizTaker.exists() and quizTaker.first().completed:
        return redirect("quiz_result", quiz_id=quiz_id)

    questions = []
    responses = []

    if quizTaker.exists():
        quizTaker = quizTaker.first()
        if quizTaker.started:
            queryset = (
                quizTaker.response_set.select_related("question").all().order_by("pk")
            )
            for response in queryset:
                questions.append(model_to_dict(response.question, exclude=["correct"]))
                responses.append(
                    model_to_dict(response, exclude=["isCorrect", "marks"])
                )
        else:
            quizTaker.started = timezone.now()
            quizTaker.save()
            shuffledQuestions = quiz.question_set.all()[::1]
            random.shuffle(shuffledQuestions)

            for question in shuffledQuestions:
                response = Response(quiztaker=quizTaker, question=question, answer="")
                response.save()
                questions.append(model_to_dict(question, exclude=["correct"]))
                responses.append(
                    model_to_dict(response, exclude=["isCorrect", "marks"])
                )
    else:
        return redirect("quiz_started", quiz_id=quiz_id)
    shuffle = quiz.isShuffle
    context = {
        "quiz": quiz,
        "questions": json.dumps(questions),
        "responses": responses,
        "shuffle": json.dumps(shuffle),
        "quizTaker": quizTaker,
    }
    return render(request, "quiz_app/quiz.html", context)


def saveResponse(request):
    if not request.user.is_authenticated:
        jsonResponse = JsonResponse({"error": "logged out"})
        jsonResponse.status_code = 403
        return jsonResponse
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        question = Question.objects.filter(pk=question).first()
        response = Response.objects.filter(quiztaker_id=quizTaker, question=question)
        isCorrect = answer == question.correct
        if isCorrect:
            response.update(answer=answer, isCorrect=True, marks=question.marks)
        else:
            response.update(answer=answer, isCorrect=False, marks=0)

    return JsonResponse({"success": "Response successfully saved"})


def completed(request):
    if not request.user.is_authenticated:
        jsonResponse = JsonResponse({"error": "logged out"})
        jsonResponse.status_code = 403
        return jsonResponse
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        quizTaker = QuizTakers.objects.get(pk=quizTaker)
        quizTaker.completed = timezone.now()
        quizTaker.save()
        context = {
            "name": request.user.full_name,
            "title": quizTaker.quiz.title,
            "started": quizTaker.started,
            "completed": quizTaker.completed,
        }
        msg_plain = render_to_string("email/test_confirmation.txt", context)
        msg_html = render_to_string("email/test_confirmation.html", context)
        send_mail(
            "Test submitted successfully",
            msg_plain,
            "webmaster@localhost",
            [request.user.email],
            html_message=msg_html,
        )
    return JsonResponse({"success": "Quiz successfully saved"})


# quiz results route
# @/quiz/<quiz_id>/result
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    quizTaker = get_object_or_404(QuizTakers, quiz_id=quiz_id, user_id=request.user.pk)
    queryset = (
        quizTaker.response_set.select_related("question").all().order_by("question_id")
    )
    questions = []
    responses = []
    for response in queryset:
        questions.append(model_to_dict(response.question))
        responses.append(model_to_dict(response))

    context = {
        "quiz": quiz,
        "questions": json.dumps(questions),
        "responses": responses,
        "quizTaker": quizTaker,
    }

    return render(request, "quiz_app/quiz_result.html", context)


def export_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    quizTaker = get_object_or_404(QuizTakers, quiz_id=quiz_id, user_id=request.user.pk)
    if not quizTaker.has_ended:
        messages.info(request, "The Test has not been submitted yet.")
        return redirect("quiz", quiz_id=quiz.quiz_id)

    responses = (
        quizTaker.response_set.select_related("question")
        .all()
        .order_by("question_id")[::1]
    )

    filename = f"Result {request.user.full_name}.xlsx"
    response = HttpResponse(
        generate_result_as_excel(request, quiz, quizTaker, responses),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={filename}"

    return response


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
            if request.user.is_authenticated:
                QuizTakers.objects.get_or_create(quiz=quiz, user=request.user)
                return redirect("quiz_instructions", quiz_id=quiz_id)
            else:
                return redirect("login")
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


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            send_verification_email(request, form)
            messages.info(
                request, "Please Confirm Your Email Address Before Continuing"
            )
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


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

