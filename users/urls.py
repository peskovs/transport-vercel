from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Autentifikācija
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Lietotāja profils
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]