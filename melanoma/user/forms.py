from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, Image


class PatientSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name','email', 'password1', 'password2']


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['age', 'gender', 'phone']


class UploadImageForm(forms.ModelForm):
    user_notes = forms.CharField(max_length=250, required=True)
    image = forms.ImageField(required=True)

    class Meta:
        model = Image
        fields = ['user_notes', 'image']
