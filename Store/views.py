from django.shortcuts import render, get_list_or_404
from .models import Item, Request, Store
from Users.models import Notication, StoreUser
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
        #Notification
        item.save()
    elif item.quantity == 0:
        Notication.objects.create(text='No item we will notify you when its available')

def alert(item):
    admins = StoreUser.objects.filter(super=True)
    items = Item.objects.filter(quantity__lte=5)
    for item in items:
        message = 'You  neeed to supply More ' + str(item.name)
        for admin in admins:
            Notication.objects.create(text=message, faculty=admin)

def search(request):
    pass




def index(request):
    return render(request, 'index.html')


#jiegwwjgiojgwgoijwoi


