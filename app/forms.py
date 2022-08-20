from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm , UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model=User
        fields = ('email',)
        
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model= User
        fields = ('email',)
        
        
class RegistrationForm(UserCreationForm):
    
    class Meta(UserCreationForm):
        model = User
        fields = ['email','name','password1','password2']

       
       
