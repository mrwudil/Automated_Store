from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UserChangeForm
from .models import Faculties


class SignupForm(UserCreationForm):
    class Meta:
        model = Faculties
        fields = ['faculty_name', 'email', 'phone', 'username']


class ProfileEditForm(UserChangeForm):
    model = Faculties
    fields = ['avatar', 'faculty_name', 'administrator', 'phone',]