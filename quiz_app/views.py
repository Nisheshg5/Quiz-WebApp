import json
import random
from json import JSONEncoder
from uuid import UUID

from django.contrib import messages
from django.db.models import F
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import datetime
from verify_email.email_handler import send_verification_email

from .forms import QuizForm, QuizPasswordForm, SignUpForm
from .models import Quiz, QuizTakers, Response

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

