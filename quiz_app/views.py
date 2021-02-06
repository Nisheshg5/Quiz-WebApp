from uuid import UUID

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import datetime

# For the signup form
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from .forms import QuizForm
from .models import Quiz


def home(request):
    id = request.GET.get("quiz_id")
    if id:
        try:
            val = UUID(id).version
            if val != 4:
                raise ValueError(0)
            if Quiz.objects.filter(pk=id).exists():
                return redirect("quiz", quiz_id=id)
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
    context = {"quiz": quiz}
    return render(request, "quiz_app/quiz.html", context)


def about(request):
    return render(request, "quiz_app/about.html")


def contact(request):
    return render(request, "quiz_app/contact.html")


def hello_there(request, name):
    return render(
        request, "quiz_app/hello_there.html", {"name": name, "date": datetime.now()}
    )

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


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
