from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.http import JsonResponse
from .models import Item, Record, Request, Store
from Users.models import Notification, StoreUser
import time


# Create your views here.


def home(request):
    items = Item.objects.all()
    return render(request, 'request.html', {'items': items})

def histoty(request):
    history = Record.objects.filter(request__faculty=request.user).order_by('-time')
    return render(request, 'history.html', {"hist": history})



def request_items(request, item_id, quantity):
    print("food")
    user = request.user
    item =  get_object_or_404(Item, id=item_id)
    alert() #Used to alert the admins  if a particular item is less than five
    check_it = Request.objects.filter(product=item, faculty=user, collected=False)
    if eligibility(request, item_id):
        if item.quantity >= quantity:
            print("quantity dai dai")
            get_it = get_object_or_404(Request, product=item, faculty=user)
            get_it.quantity += quantity
            get_it.save()
            item.quantity -= quantity
            item.save()
            return JsonResponse({"message": "your request is updated successfully"})
        elif item.quantity < quantity and item.quantity != 0:
            print("quantity ba dai dai ba")
            Request.objects.create(product=item, quantity=item.quantity, faculty=user) 
            item.quantity -= quantity
            # Notification.objects.create(text='Only two ', faculty=user)
            item.save()
            return JsonResponse({"message": f'{item.name} requested successfully'}, status=200)
        elif item.quantity == 0:
            print("babu")
            Notification.objects.create(text='No item we will notify you when its available', faculty=user)
            return JsonResponse({"message": "No item we will notify you when its available"}, status=200)
        else:
            print("creating sabo")
            Request.objects.create(product=item, quantity=quantity, faculty=user)
            item.quantity -= quantity
            item.save()
            return JsonResponse({"message": f'{item.name} requested successfully'}, status=200)
    else:
        JsonResponse({"message": "you have reached your request allowed allocation"}, status=200)
    


def eligibility(request, item_id):
    user = request.user
    item =  get_object_or_404(Item, id=item_id)
    records = Record.objects.filter(request__product=item, request__faculty=user, request__collected=True, time__gt=int(item.restriction_time))
    number_of_request = records.count()
    if number_of_request >= item.restriction:
        return False
    else:
        return True

def submit_request(request):
    user = request.user
    all_request = Request.objects.filter(faculty=user, collected=False)
    for the_request in all_request:
        if the_request.quantity <= request.product.quanty:
            the_request.message = 'Given'
            the_request.save()
        else:
             the_request.message = str(the_request.quantity) + 'Requested' + str(the_request.product.quantity) + 'Given'
             the_request.quantity = the_request.product.quantity
             the_request.save()
    return render(request, 'next.html', {"items": the_request})

def alert():
    """Used to alert the admins  if a particular item is less than five"""
    admins = StoreUser.objects.filter(is_superuser=True)
    items = Item.objects.filter(quantity__lte=5)
    for item in items:
        message = 'You  neeed to supply More ' + str(item.name)
        for admin in admins:
            Notification.objects.create(text=message, faculty=admin)


def alert_faculty(item_id):
    item = Item.objects.filter(id=item_id)
    message = str(item.name)+ 'Has now arrived  you can now order your remaining'
    Notification.objects.create(text='The')


def search(request):
    pass




def index(request):
    return render(request, 'index.html')


#jiegwwjgiojgwgoijwoi


