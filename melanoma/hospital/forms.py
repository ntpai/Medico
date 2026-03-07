from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from user.models import HospitalProfile, DoctorProfile

User = get_user_model()

class HospitalUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class HospitalProfileForm(forms.ModelForm):
    class Meta:
        model = HospitalProfile
        fields = ["hospital_name", "license", "address", "contact_email"]

class DoctorUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['license' , 'specialization']