from django.urls import path
from . import views

urlpatterns = [
    path('', views.hospital_dashboard, name="hospital_home"),
    path('signup/', views.signup, name="hospital_signup"),
    path('signin/', views.signin, name="hospital_signin"),
    path('viewprofile/', views.view_profile, name="hospital_view_profile"),
    path('add_doctor/', views.add_doctor, name="add_doctor"),
    path('view_doctors/', views.view_doctors, name="view_doctors"),
    path('logout/', views.log_out, name='hospital_logout'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/signin', views.doctor_signin, name='doctor_signin'),
    path('test-alerts/', views.test_notifications, name='test_notifications'),
    path('hospital_appointments/', views.hospital_appointment_list, name='hospital_appointments'),
    path('doctor_appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/images/<int:patient_id>/', views.view_patient_images, name='view_patient_images'),
]