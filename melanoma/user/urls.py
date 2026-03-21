from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user_home'),
    path('signin/', views.signin, name='user_signin'),
    path('signup/', views.signup, name='user_signup'),
    path('uploadimage/', views.upload_image, name='upload_image'),
    path('logout/', views.log_out, name='user_logout'),
    path('image_result/', views.image_result, name='user_image_result'),
    path('hospitals/', views.patient_hospital_list, name='patient_hospitals_list'),
    path('hospitals/<int:hospital_id>/', views.patient_doctors_list, name='patient_doctors_list'),
    path('book/<int:doctor_id>/', views.book_doctor, name='patient_book_doctor'),
    path('api/booked-times/<int:doctor_id>/<str:booking_date>/', views.get_booked_times, name='get_booked_times'),
]