from django.shortcuts import render, get_list_or_404
from .models import Item, Request, Store, Record
from Users.models import Notication
import time


# Create your views here.


def home(request):
    items = Item.objects.all()
    return render(request, 'home.html', {'items': items})

def histoty(request):
    history = Record.objects.filter(request__faculty=request.user).order_by('-time')
    return render(request, 'history.html', {"hist": history})

def request_items(request, item_id, quantity):
    user = request.user
    store = get_list_or_404(Store, id=1)
    item = Item.objects.filter(id=item_id)
    if item in store.items and item.quantity >= quantity:
        Request.objects.creeate(product=item, quantity=quantity, faculty=user)
        item.quantity -= quantity
        item.save()
    elif item.quantity < quantity and item.quantity != 0:
        Request.objects.create(products=item, quanntity=item.quantity, faculty=user)
        item.quantity -= quantity
        Notification
        item.save()
    elif item.quantity == 0:
        Notication

def alert(item):
    pass

def search(request):
    pass




