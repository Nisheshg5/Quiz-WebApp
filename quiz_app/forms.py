from django import forms
from django.forms import fields

from .models import Quiz


class QuizForm(forms.Form):
    quiz_id = forms.CharField(
        max_length=36,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Enter Quiz Code"}),
    )
    # class Meta:
    #     model = Quiz
    #     fields = [
    #         'quiz_id'
    #     ]
