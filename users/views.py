from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView, UpdateView, DetailView
from .forms import UserRegistrationForm, UserLoginForm, RenterProfileForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.urls import reverse_lazy
from .models import RenterProfile

# Create your views here.
class CreateUserView(FormView):

    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")
    
    def form_valid(self, form):
        # Save the user
        user = form.save()
        
        # No need to explicitly create a RenterProfile here
        # The post_save signal will handle it automatically
        
        # Add success message
        messages.success(self.request, "Account created successfully! You can now log in.")
        
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # Add error message
        messages.error(self.request, "There was an error with your registration. Please check the form and try again.")
        
        return super().form_invalid(form)


class LoginUserView(LoginView):

    template_name = "users/login.html"
    authentication_form = UserLoginForm

    def form_invalid(self, form: AuthenticationForm) -> HttpResponse:
        messages.warning(self.request, "Invalid Username or Password. Please try again.")
        return super().form_invalid(form)
    
    def form_valid(self, form):
        # Call the parent class form_valid method first to log the user in
        response = super().form_valid(form)
        
        # Check if the user has a renter profile, create one if not
        try:
            self.request.user.renter_profile
        except RenterProfile.DoesNotExist:
            RenterProfile.objects.create(user=self.request.user)
        
        return response
    
class ChooseUserRoleView(LoginRequiredMixin, TemplateView):

    template_name = "users/welcome.html"

class RenterProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = RenterProfile
    form_class = RenterProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user.renter_profile

class RenterProfileView(LoginRequiredMixin, DetailView):
    model = RenterProfile
    template_name = 'users/profile.html'
    context_object_name = 'profile'
    
    def get_object(self, queryset=None):
        return self.request.user.renter_profile

    



    



