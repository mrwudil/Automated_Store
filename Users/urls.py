from django.urls import path
from .views import signup_view, edit_view

app_name = 'users'
  
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('edit/', edit_view, name='edit'),
]