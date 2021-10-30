from django.shortcuts import render, redirect
from .forms import SignupForm, ProfileEditForm
from django.contrib.auth import authenticate,  login

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            authenticate(username=username, password=password)
            return redirect('users:signup')
    else:
        form = SignupForm()
        return render(request, 'registration/signup.html', {'form':form})


def edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:signnup')

 