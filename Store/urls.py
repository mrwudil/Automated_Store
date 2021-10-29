from django.urls import path
from .views import index, home, request_items

app_name = 'store'

urlpatterns = [
    path('', index, name='index'),
    path('request', home, name='home'),
    path('give-me/<int:item_id>/<int:quantity>', request_items, name='give_me')
]