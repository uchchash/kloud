from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Member


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

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.NumberInput(attrs={
        'class': 'border p-2 rounded w-full',
        'placeholder': 'Enter 6-digit OTP'
    }))


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg focus:ring focus:ring-blue-200'
            field.widget.attrs['placeholder'] = field.label

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('image', 'date_of_birth', 'gender')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg focus:ring focus:ring-blue-200'
            field.widget.attrs['placeholder'] = field.label

class EmailChangeRequestForm(forms.Form):
    updated_email = forms.EmailField(label="New Email")
    
class PasswordChangeRequestForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

