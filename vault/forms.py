from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg focus:ring focus:ring-blue-200'
            field.widget.attrs['placeholder'] = field.label    

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg focus:ring focus:ring-blue-200'
            field.widget.attrs['placeholder'] = field.label    