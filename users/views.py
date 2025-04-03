from django.shortcuts import render
from django.views.generic import FormView
from .forms import UserRegistrationForm
from django.contrib.auth.models import User

# Create your views here.
class CreateUserView(FormView):

    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = "users:login"



    



