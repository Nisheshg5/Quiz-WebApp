import json
import random
from json import JSONEncoder
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import datetime
from django.views import generic
from verify_email.email_handler import send_verification_email

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
    quizTaker = QuizTakers.objects.filter(quiz=quiz, user=request.user)
    if quizTaker.exists() and quizTaker.first().completed:
        return redirect("quiz_result", quiz_id=quiz_id)
    if quiz.has_ended:
        return redirect("quiz_ended", quiz_id=quiz_id)

    if not request.user.is_authenticated:
        return redirect("login")

    questions = []
    responses = []

    if quizTaker.exists():
        quizTaker = quizTaker.first()
        if quizTaker.started:
            queryset = quizTaker.response_set.all().order_by("pk")
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
    print(context)
    return render(request, "quiz_app/quiz.html", context)

# Creating dummy function 

# def quiz(request, quiz_id):
#     context = {'quiz': <Quiz: id: 24cf6d26-655d-4fe3-a377-3c8b55a3ba00, title: Quiz Title>, 'questions': '[{"id": 17, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "How array is passed as argument to a Function In C?", "choice_1": "Value of elements in array", "choice_2": "First element of the array", "choice_3": "Base address of the array", "choice_4": "Address of the last element of array", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 5, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "What is the size of an float data type?", "choice_1": "4 Bytes", "choice_2": "8 Bytes", "choice_3": "Depends on the system/compiler", "choice_4": "Cannot be determined", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 13, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "what is a pointer", "choice_1": "A keyword used to create variables", "choice_2": "A variable that stores address of an instruction", "choice_3": "A variable that stores address of other variable", "choice_4": "All of the above", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 25, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "What do the following declaration signify?\\r\\n\\r\\nfloat (*pf)();", "choice_1": "pf is a pointer to function.", "choice_2": "pf\\u00a0is a function pointer.", "choice_3": "pf\\u00a0is a pointer to a function which return\\u00a0float", "choice_4": "pf\\u00a0is a function of pointer variable.", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 26, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "What do the following declaration signify?\\r\\n\\r\\ndouble *ptr[5];", "choice_1": "ptr is a pointer to an array of 5 double pointers.", "choice_2": "ptr\\u00a0is a array of 5 pointers to doubles.", "choice_3": "ptr\\u00a0is a array of 5 double pointers.", "choice_4": "ptr is a array 5 pointers.", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 4, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "Local variables are stored in which area of memory", "choice_1": "Heap", "choice_2": "Stack", "choice_3": "Queue", "choice_4": "Linklist", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 24, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "What do the following declaration signify?\\r\\n\\r\\nchar **p;", "choice_1": "p\\u00a0is a pointer to pointer.", "choice_2": "p\\u00a0is a pointer to a\\u00a0char\\u00a0pointer.", "choice_3": "p\\u00a0is a function pointer.", "choice_4": "p is a member of function pointer.", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 22, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "Header file to use log(3) in C program", "choice_1": "#include<conio.h>", "choice_2": "#include<math.h>", "choice_3": "#include<stdlib.h>", "choice_4": "#include<dos.h>", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 16, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "How many times the\\u00a0while\\u00a0loop will get executed.#include<stdio.h>\\r\\nint main()\\r\\n{\\r\\n    int j=1;\\r\\n    while(j <= 255)\\r\\n    {\\r\\n       
#     printf(\\"%c %d\\\\n\\", j, j);\\r\\n        j++;\\r\\n    }\\r\\n    return 0;\\r\\n}", "choice_1": "Infinite times", "choice_2": "255 times", "choice_3": "256 
#     times", "choice_4": "254 times", "choice_5": "", "marks": 1, "isShuffle": true}, {"id": 1, "quiz": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00", "title": "The preprocessor directive which is used to end the scope of #ifdef.", "choice_1": "#ifdef.", "choice_2": "#elif", "choice_3": "#endif", "choice_4": "#if", "choice_5": "", "marks": 1, "isShuffle": true}]', 'responses': [{'id': 302, 'quiztaker': 48, 'question': 17, 'answer': ''}, {'id': 303, 'quiztaker': 48, 'question': 5, 'answer': ''}, {'id': 304, 'quiztaker': 48, 'question': 13, 'answer': ''}, {'id': 305, 'quiztaker': 48, 'question': 25, 'answer': ''}, {'id': 306, 'quiztaker': 48, 'question': 26, 'answer': ''}, {'id': 307, 'quiztaker': 48, 'question': 4, 'answer': ''}, {'id': 308, 'quiztaker': 48, 'question': 24, 'answer': ''}, {'id': 309, 'quiztaker': 48, 'question': 22, 'answer': '#include<math.h>'}, {'id': 310, 'quiztaker': 48, 'question': 16, 'answer': '255 times'}, {'id': 311, 'quiztaker': 48, 'question': 1, 'answer': ''}], 'shuffle': 'true', 'quizTaker': <QuizTakers: QuizTakers object (48)>}:

def saveResponse(request):
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

    return HttpResponse("{}", content_type="application/json")


def completed(request):
    if request.method == "POST":
        quizTaker = request.POST.get("quizTaker")
        quizTaker = QuizTakers.objects.filter(pk=quizTaker)
        quizTaker.update(completed=timezone.now())

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
            if request.user.is_authenticated:
                QuizTakers.objects.create(quiz=quiz, user=request.user)
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
