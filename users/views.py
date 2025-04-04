from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import FormView
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy

# Create your views here.
class CreateUserView(FormView):

    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")


class LoginUserView(LoginView):

    template_name = "users/login.html"
    authentication_form = UserLoginForm

    def form_invalid(self, form: AuthenticationForm) -> HttpResponse:
        messages.warning(self.request, "Invalid Username or Password. Please try again.")
        print(list(messages.get_messages(self.request)))
        return super().form_invalid(form)
    


    



