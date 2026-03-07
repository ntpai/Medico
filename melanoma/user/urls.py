from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user_home'),
    path('signin/', views.signin, name='user_signin'),
    path('signup/', views.signup, name='user_signup'),
    path('uploadimage/', views.upload_image, name='upload_image'),
    path('logout/', views.log_out, name='user_logout'),
    path('image_result/', views.image_result, name='user_image_result'),
]