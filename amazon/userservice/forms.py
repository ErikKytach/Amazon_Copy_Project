from django.contrib.auth.forms import *
from django import forms
from userservice.models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)
    phonenumber = forms.CharField(required = True, max_length=30)
    first_name = forms.CharField(required = True, max_length=100)
    last_name = forms.CharField(required = True, max_length=100)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phonenumber", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded'

    #def __str__(self):
     #   return f"email: {email}; phone: {phonenumber}; first name: {first_name}; last name: {last_name}; password1: {password1}; password2: {password2}"

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded'
        })