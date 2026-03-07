from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from .forms import *

User = get_user_model()

# user type checkers for restricting to hospital and doctor dashboards
def doctor_required(view_func):
    @wraps(view_func)
    def wrapped_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('doctor_signin')

        if not getattr(request.user, "is_doctor", False):
            return redirect('doctor_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapped_func

def hospital_admin_required(view_func):
    @wraps(view_func)
    def wrapped_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('hospital_signin')

        if not getattr(request.user, "is_hospital_admin", False):
            return redirect('user_home')

        return view_func(request, *args, **kwargs)
    return wrapped_func

# Hospital Dashboard views
def redirect_user(user):
    if user.is_doctor:
        return redirect("doctor_home")
    elif user.is_hospital_admin:
        return redirect("hospital_home")
    else:
        return redirect("home")

def index(request):
    return render(request, "hospital/index.html")

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return redirect_user(user)

        except User.DoesNotExist:
            messages.error(request, "No user found!")
            return redirect('hospital_signup')

    return render(request, "hospital/signin.html")

def signup(request):
    if request.method == 'POST':
        user_form = HospitalUserForm(request.POST)
        hospital_profile_form = HospitalProfileForm(request.POST)

        if user_form.is_valid() and hospital_profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_hospital_admin = True
            user.save()

            hospital_profile = hospital_profile_form.save(commit=False)
            hospital_profile.user = user
            hospital_profile.save()

            messages.info(request, "Registration Completed! Please wait for admin approval.")
            login(request, user)
            return redirect("hospital_signin")
    else:
        user_form = HospitalUserForm()
        hospital_profile_form = HospitalProfileForm()
    context = {
        'user_form': user_form,
        'hospital_profile_form': hospital_profile_form
    }

    return render(request, "hospital/signup.html", context=context)

@login_required
def view_profile(request):
    profile_obj = HospitalProfile.objects.filter(user_id=request.user.pk).values()

    profile =  {
        'hospital_name' : profile_obj[0]['hospital_name'],
        'license': profile_obj[0]['license'],
        'address': profile_obj[0]['address'],
        'contact_email': profile_obj[0]['contact_email'],
        'is_approved': profile_obj[0]['is_approved'],
    }

    return render(request, 'hospital/view_profile.html', context=profile)

@login_required
def log_out(request):
    logout(request)
    return redirect('hospital_home')

# Doctor Dashboard views
@hospital_admin_required
def add_doctor(request):
    hospital_ref = HospitalProfile.objects.get(user_id=request.user.pk)
    if request.method == "POST":
        doctor_user_form = DoctorUserForm(request.POST)
        doctor_profile_form = DoctorProfileForm(request.POST)
        if doctor_user_form.is_valid() and doctor_profile_form.is_valid():
            user = doctor_user_form.save(commit=False)
            user.is_doctor = True
            user.save()

            doctor_profile = doctor_profile_form.save(commit=False)
            doctor_profile.user = user
            doctor_profile.hospital = hospital_ref
            doctor_profile.save()

            messages.info(request, "New doctor registered.")
            return redirect('hospital_home')
    else:
        doctor_user_form = DoctorUserForm()
        doctor_profile_form = DoctorProfileForm()
    context = {
        'user_form': doctor_user_form,
        'profile_form': doctor_profile_form,
    }
    return render(request, "hospital/add_doctor.html", context=context)

@login_required
def view_doctors(request):
    # NOTE:
    # Hospital needs to be used when retrieving the data from models because the HospitalProfile uses CustomUser
    # as its AbstractUser for authentication. Therefore, user_id should be used to retrieve the HospitalProfile
    # not the primary key on the HospitalProfile, pk refers to the row of the HospitalProfile but the user_id refers
    # to the current user's pk id from CustomUsers model
    hospital_ref = HospitalProfile.objects.get(user=request.user)
    doctors_list = DoctorProfile.objects.filter(hospital=hospital_ref).select_related('user')
    doctors_count = doctors_list.count()
    context = {
        'doctors_count' : doctors_count,
        'doctors_list': doctors_list,
    }
    return render(request, "hospital/view_doctors.html", context=context)

# Doctor dashboard
@doctor_required
def doctor_dashboard(request):
    # TO ADD
    # no. of appointments
    return render(request, "doctor/dashboard.html")

def doctor_signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.get(email=email)
        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('doctor_signin')
    return render(request, "doctor/signin.html")