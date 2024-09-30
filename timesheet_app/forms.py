from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    employee_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password', 'employee_name']