import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from .forms import *
from user.models import *
from django.utils import timezone

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


def hospital_dashboard(request):

    today = timezone.localtime(timezone.now()).date()

    hospital_profile_id = HospitalProfile.objects.filter(user_id=request.user.pk).first()

    total_doctors = DoctorProfile.objects.filter(hospital_id=hospital_profile_id).count()

    # Count ALL appointments across the entire hospital for today
    appointments_today = Appointment.objects.filter(
        appointment_date__year=today.year,
        appointment_date__month=today.month,
        appointment_date__day=today.day
    ).count()

    context = {
        'total_doctors': total_doctors,
        'appointments_today': appointments_today,
    }

    return render(request, 'hospital/index.html', context)

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                messages.success(request, "Signin success.")
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

            messages.success(request, "Registration Completed! Please Signin.")
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

            messages.success(request, "New doctor registered.")
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
    doctor_profile = DoctorProfile.objects.get(user=request.user)

    today = timezone.localtime(timezone.now()).date()

    todays_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        appointment_date__year=today.year,
        appointment_date__month=today.month,
        appointment_date__day=today.day
    )

    total_today = todays_appointments.count()

    pending_today = todays_appointments.filter(status='Pending').count()
    completed_today = todays_appointments.filter(status='Completed').count()

    context = {
        'doctor': doctor_profile,
        'today': today,
        'total_today': total_today,
        'pending_today': pending_today,
        'completed_today': completed_today,
    }

    return render(request, 'doctor/dashboard.html', context)

def doctor_signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.get(email=email)
        if user is not None and user.check_password(password):
            login(request, user)
            messages.success(request, "Signin successfully.")
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('doctor_signin')
    return render(request, "doctor/signin.html")

def test_notifications(request):
    messages.success(request, "Payment successful! Your appointment is confirmed.")
    messages.error(request, "Oops! You cannot book an appointment in the past.")
    messages.warning(request, "Please update your profile information.")
    messages.info(request, "Dr. Smith has joined City Hospital.")


    return render(request, "hospital/test_notifying.html")


def hospital_appointment_list(request):
    hospital = HospitalProfile.objects.filter(user=request.user).first()
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        appointment_date=today,
        doctor__hospital=hospital
    ).order_by('-appointment_date', 'appointment_time')

    if request.method == "POST":
        appt_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')

        appt = get_object_or_404(Appointment, id=appt_id, doctor__hospital=hospital)
        appt.status = new_status
        appt.save()
        return redirect('hospital_appointments')

    return render(request, 'hospital/appointments.html', {'appointments': appointments, "today": today})


def view_patient_images(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    images = Image.objects.filter(user_id=patient.user).order_by('-upload_at')

    return render(request, 'doctor/view_images.html', {
        'patient': patient,
        'images': images
    })

def doctor_appointments(request):
    doctor_profile = DoctorProfile.objects.get(user=request.user)

    today = timezone.now().date()
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')

        try:
            appt_to_update = Appointment.objects.get(id=appointment_id, doctor=doctor_profile)
            appt_to_update.status = new_status
            appt_to_update.save()

            return redirect('doctor_appointments')
        except Appointment.DoesNotExist:
            pass
    appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        # appointment_date=today
    ).order_by('appointment_time')

    context = {
        'appointments': appointments,
        'today': today,
        'doctor': doctor_profile
    }

    return render(request, 'doctor/appointments.html', context)


def view_patient_images(request, patient_id):
    # 1. Find the specific patient profile
    patient = get_object_or_404(Patient, id=patient_id)

    # 2. Fetch images linked to the patient's user account
    # We order by '-upload_at' to get Newest -> Oldest as you requested
    images = Image.objects.filter(user_id=patient.user).order_by('-upload_at')

    return render(request, 'doctor/view_images.html', {
        'patient': patient,
        'images': images
    })