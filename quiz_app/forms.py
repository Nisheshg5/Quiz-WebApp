from django import forms
from django.forms import fields

from .models import Account, Quiz


class QuizForm(forms.Form):
    quiz_id = forms.CharField(
        max_length=36,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter Quiz Code",
                "value": "24cf6d26-655d-4fe3-a377-3c8b55a3ba00"
            }
        ),
    )
    # class Meta:
    #     model = Quiz
    #     fields = [
    #         'quiz_id'
    #     ]


class QuizPasswordForm(forms.ModelForm):
    password = forms.CharField(
        max_length=32,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "value": "password"}
        ),
    )

    class Meta:
        model = Quiz
        fields = ["password"]


class SignupForm(forms.Form):
    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg", 
                "placeholder": "Enter Email"
            }
        )
    )
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter username"
            }
        )
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg", 
                "placeholder": "Enter password"
            }
        )
    )
    confirmPassword = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg", 
                "placeholder": "Enter password again"
            }
        )
    )
    class Meta:
        model = Account
        fields = [
            'username',
            'email',
            'password'
        ]
