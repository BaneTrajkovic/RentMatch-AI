"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

app_name = "users"
urlpatterns = [
    path("register/", views.CreateUserView.as_view(), name="register"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("welcome/", views.ChooseUserRoleView.as_view(), name="welcome"),
    path("profile/", views.RenterProfileView.as_view(), name="profile"),
    path("profile/edit/", views.RenterProfileUpdateView.as_view(), name="profile_edit"),
    path("landlord/", login_required(TemplateView.as_view(template_name="users/landlord.html")), name="landlord"),
    path("investor/", login_required(TemplateView.as_view(template_name="users/investor.html")), name="investor"),
]
