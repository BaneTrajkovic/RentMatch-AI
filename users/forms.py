from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from .models import RenterProfile

class UserRegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
        
        # Terms checkbox
        self.fields['terms_agreement'] = forms.BooleanField(
            required=True,
            label='I agree to RentMatch\'s <a href="#" class="link-gold">Terms</a> and <a href="#" class="link-gold">Privacy Policy</a>'
        )
        
        # Layout
        self.helper.layout = Layout(
            Div(Field('username', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Field('email', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Field('password1', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Field('password2', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Submit('submit', 'Create Account', css_class='btn btn-gold btn-lg py-3 w-100'), css_class='d-grid mb-4'),
            HTML('<div class="text-center"><p class="mb-0">Already have an account? <a href="#" class="link-gold">Log In</a></p></div>')
        )


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ["username", "password"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
        
        # Layout
        self.helper.layout = Layout(
            Div(Field('username', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Field('password', css_class='form-control', wrapper_class='form-floating mb-4')),
            Div(Submit('submit', 'Log In', css_class='btn btn-gold btn-lg py-3 w-100'), css_class='d-grid mb-4'),
            HTML('<div class="text-center"><p class="mb-0">Already have an account? <a href="#" class="link-gold">Log In</a></p></div>')
        )

class RenterProfileForm(forms.ModelForm):
    class Meta:
        model = RenterProfile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'employment_start_date': forms.DateInput(attrs={'type': 'date'}),
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(RenterProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['date_of_birth', 'employment_start_date', 'move_in_date']:
                field.widget.attrs.update({'class': 'form-control'})