from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Gender(models.TextChoices):
    Male = 'M', 'Male'
    Female = 'F', 'Female'
    PREFER_NOT_TO_SAY = 'U', 'Prefer not to say'

class CustomUser(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_hospital_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class HospitalProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=50, unique=True)
    license = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    contact_email = models.EmailField()
    is_approved = models.BooleanField(default=False)
    date_of_registration = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Approved" if self.is_approved else "Approval Pending"
        return f"{self.hospital_name} {status}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr.{self.user.last_name} - {self.hospital.hospital_name}"

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(
        max_length=1,
        choices=Gender,
        default=Gender.PREFER_NOT_TO_SAY,
        help_text="Select your gender."
    )
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"username:{self.user.username} gender: {self.get_gender_display()}"

def upload_to(instance, image_name):
    return f"images/{image_name}"

class Image(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=True, blank=True)
    upload_at = models.DateTimeField(auto_now_add=True)
    user_notes = models.CharField(max_length=250)
    image = models.ImageField(upload_to=upload_to,blank=True, null=True)
    accuracy = models.FloatField(default=0.0)
    result = models.CharField(max_length=20, default="Pending")

class Appointment(models.Model):
    STATUS_CHOICE  = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="my_appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="doctor_appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason_for_visit = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.first_name} with Dr. {self.doctor.user.first_name} on \
            {self.appointment_date} - {self.appointment_time}"