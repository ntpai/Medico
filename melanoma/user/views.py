from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from functools import wraps
from detection_model.predictor import predict_melanoma
from detection_model.visualizer import visualizer
from .forms import *
from .models import Image, DoctorProfile, HospitalProfile, Appointment
from datetime import datetime, date
User = get_user_model()

# check if the user type is patient or not
def check_user(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Signin/Signup to see the features of the website.")
            return redirect('user_signin')
        if getattr(request.user, "is_patient", False):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Another user type detected.")
            if getattr(request.user, "is_doctor", False):
                return redirect('doctor_dashboard')
            elif getattr(request.user, "is_hospital_admin", False):
                return redirect('hospital_home')
            else:
                return redirect('home')
    return wrapper

@check_user    
def index(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        print(f"Login ID: {user_id}")
    return render(request, 'users/index.html')

def signup(request):
    if request.method == 'POST':
        user_form = PatientSignupForm(request.POST)
        profile_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            
            user = user_form.save(commit=False)
            user.is_patient = True
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            return redirect('user_home')
    else: 
        user_form = PatientSignupForm()
        profile_form = PatientProfileForm()
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/signup.html', context=context)

def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                if user.is_superuser or user.is_patient:
                    return redirect('user_home')
                else:
                    messages.error(request, "Invalid signin for user")
            else:
                return redirect('user_signin')
        except User.DoesNotExist:
            messages.error(request, "No user found! Sign up a new account.")
            return redirect('user_signup')

    return render(request, "users/signin.html")

@login_required
def log_out(request):
    logout(request)
    return redirect('user_home')

@login_required
def upload_image(request):
    if request.method == "POST":
        form = UploadImageForm(request.POST, request.FILES)
        user = get_user_model()
        patient_ref = user.objects.get(pk=request.user.id)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user_id = patient_ref
            form_instance.save()
            messages.success(request, "Image uploaded successfully.")
            return redirect('user_image_result')
    else:
        form = UploadImageForm()
    return render(request, 'users/upload_image.html', {'form':form})

@login_required
def image_result(request):
    current_user_id = request.user.id
    image_path = Image.objects.filter(user_id=current_user_id).order_by('-upload_at').first()
    prediction = predict_melanoma(image_path.image.path)
    visuals = visualizer(image_path.image.path)
    """
    Prediction givens 
    label: Benign | Malignant
    probability: Probability of the result being Benign or Malignant     
    features: list of extracted values used by predictor to determine if the given image has 
            benign or malignant result
    message: Message from predictor(can contain error or success message
    """
    if prediction['label']  != "Error":
        context = {
            'is_valid': True,
            'image_path': image_path,
            'contour_image': visuals['contour_image'],
            'label': prediction['label'],
            'message': prediction['message'],
            'features': prediction['features'],
            'accuracy': prediction['probability']
        }
    else:
        context = {
            'is_valid': False,
            'message': prediction['message'],
            'label': "Error"
        }
    return render(request, 'users/image_result.html',context=context)

@login_required
def patient_hospital_list(request):
    hospitals = HospitalProfile.objects.filter(is_approved=True)
    return render(request, "users/hospital_list.html", {'hospitals': hospitals})

@login_required
def patient_doctors_list(request, hospital_id):
    doctors = DoctorProfile.objects.filter(hospital_id=hospital_id)
    return render(request, 'users/doctors_list.html', {'doctors': doctors})

@login_required
def book_doctor(request, doctor_id):
    doctor_data = DoctorProfile.objects.filter(user_id=doctor_id).select_related('user')

    doctor = DoctorProfile.objects.filter(user_id=doctor_id).first()
    patient = request.user.patient

    if request.method == "POST":
        booking_date = request.POST.get('appointment_date')
        time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        today = date.today()

        compare_date = datetime.strptime(booking_date, "%Y-%m-%d").date()

        if compare_date <= today:
            messages.error(request, "Appointment must be booked one day before")
            return redirect('patient_book_doctor', doctor_id=doctor_id)
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=booking_date,
            appointment_time=time,
            reason_for_visit=reason
        )
        print("booked")
        messages.success(request, "Appointment confirmed!")
        return redirect("user_home")
    return render(request, 'users/book_appointment.html', {'doctor_data': doctor_data})


def get_booked_times(request, doctor_id, booking_date):
    print(doctor_id, booking_date)
    # 1. Find all appointments for this specific doctor on the chosen date
    doctor_profile = DoctorProfile.objects.filter(user_id=doctor_id).first()
    appointments = Appointment.objects.filter(doctor_id=doctor_profile.pk   , appointment_date=booking_date)

    # 2. Extract just the times, formatted to match your HTML values (e.g., "09:30")
    # strftime('%H:%M') converts the Python Time object into a simple text string
    booked_times = [app.appointment_time.strftime('%H:%M') for app in appointments]

    # 3. Send it back to the browser as raw data
    return JsonResponse({'booked_times': booked_times})