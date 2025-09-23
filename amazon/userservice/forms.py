from django.contrib.auth.forms import *
from django import forms
from userservice.models import *

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)
    phonenumber = forms.CharField(required = True, max_length=30)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phonenumber", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded'

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded'
        })