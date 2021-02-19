from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import fields

from .models import Account, Quiz


class QuizForm(forms.Form):
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Email",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Password",
            }
        ),
    )
    key = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "XXXXXX",
                "style": "text-transform:uppercase",
            }
        ),
    )
    # class Meta:
    #     model = Quiz
    #     fields = [
    #         'quiz_id'
    #     ]


class QuizPasswordForm(forms.ModelForm):
    key = forms.CharField(
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "XXXXXX",
                "style": "text-transform:uppercase",
            }
        ),
    )

    class Meta:
        model = Quiz
        fields = ["key"]


class SignUpForm(UserCreationForm):
    class Meta:
        model = Account
        fields = (
            "full_name",
            "email",
        )
