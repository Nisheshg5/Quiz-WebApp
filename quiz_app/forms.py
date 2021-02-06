from django import forms
from django.forms import fields

from .models import Quiz


class quizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
			'quiz_id'
		]
