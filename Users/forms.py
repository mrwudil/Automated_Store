from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UserChangeForm
from .models import StoreUser


class SignupForm(UserCreationForm):
    class Meta:
        model = StoreUser
        fields = ['faculty_name', 'email', 'phone', 'username']


class ProfileEditForm(UserChangeForm):
    model = StoreUser
    fields = ['avatar', 'faculty_name', 'administrator', 'phone',]