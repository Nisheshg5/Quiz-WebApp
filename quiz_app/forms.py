from django import forms
from django.forms import fields

from .models import Quiz


class quizForm(forms.ModelForm):
    pass
    # class Meta:
    #     model = Quiz
    #     fields = [
    #         'title'
    #     ]
