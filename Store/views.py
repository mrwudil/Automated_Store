from itertools import product
import re
from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .models import Item, Record, Request, Store, Category
from .forms import AddItemForm, AddCategoryForm
from django.views.generic import UpdateView
from django.views.generic.edit import FormView
from Users.models import Notification, StoreUser
from datetime import datetime, timedelta
import time
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import random
from .forms import ValidateForm
from Users.forms import ChangeUserForm
# Create your views here.


def home(request):
    items = Item.objects.all()
    return render(request, 'request.html', {'items': items})


def histoty(request):
    history = Record.objects.filter(
        request__faculty=request.user).order_by('-time')
    return render(request, 'history.html', {"hist": history})


@login_required
def request_items(request, item_id, quantity):
    print("nazo nan")
    user = request.user
    item = get_object_or_404(Item, id=item_id)
    check_it = Request.objects.filter(
        product=item, faculty=user, collected=False)
    print("checking elili")
    print(eligibility(request, item_id, quantity))
    the_eligible = eligibility(request, item_id, quantity)
    if the_eligible:
        print("i am eligible")
        if check_it.exists():
            print("it exist")
            get_it = get_object_or_404(
                Request, product=item, faculty=user, collected=False)
            get_it.quantity = quantity
            get_it.save()
            return JsonResponse({"message": 'request updated successfully'}, status=200)
        else:
            Request.objects.create(
                product=item, faculty=user, quantity=quantity)
            requested_item = get_object_or_404(
                Request, product=item, faculty=user)
            return JsonResponse({"message": 'request created successfully'}, status=200)
    else:
        print("not eligible")
        return JsonResponse({"eligilbility": "you have reached the limit of your requests", "dataType": "json"}, status=200)


def eligibility(request, item_id, the_quantity):
    user = request.user
    item = get_object_or_404(Item, id=item_id)
    print(item.restriction_time)
    restriction_number = item.restriction
    records = Request.objects.filter(product=item, faculty=user, collected=True, date__gte=datetime.now(
    ) - timedelta(days=int(item.restriction_time))).all()
    number_of_request = records.count()
    number_of_request += the_quantity
    print(sum([i.quantity for i in records], the_quantity))
    print(item.restriction)
    print(sum([i.quantity for i in records], the_quantity) >= item.restriction)
    if sum([i.quantity for i in records], the_quantity) > item.restriction:
        return False
    else:
        return True


def validate(request):
    form = ValidateForm()
    if 'code' in request.GET:
        code = request.GET.get("code")
        record = Record.objects.filter(request_num=code)
        validated = False
        if record.exists():
            the_record = get_object_or_404(Record, request_num=code)
            validated = True
            return_value = after_validate(request, the_record.id, validated)
            return return_value
        else:
            return_value = after_validate(request,  validated)
            return return_value
    else:
        return render(request, "validate.html", {"form": form})


def after_validate(request, record_id=None, validated=False):
    if validated:
        print(record_id)
        record = get_object_or_404(Record, id=record_id)
        items = record.request.all()
        return render(request, "after_validate.html", {"validate": validated, "record_id": record_id, "items": items})
    return render(request, "after_validate.html", {"validate": validated})


def approve(request, record_id):
    record = get_object_or_404(Record, id=record_id, collected=False)
    record.collected = True
    record.save()
    all_request = record.request.all()
    for request in all_request:
        quantity = request.quantity
        product = request.product
        product.quantity -= quantity
        product.save()
    return JsonResponse({"message": "approved"}, status=200)


@login_required
def submit_request(request):
    user = request.user
    if Request.objects.filter(faculty=user, collected=False).exists():
        alert()  # check if any item's quantity is low and alert the admins
        all_request = Request.objects.filter(
            faculty=user, collected=False).all()
        for the_request in all_request:
            print(the_request.product.name)
            if the_request.quantity <= the_request.product.quantity:
                the_request.message = 'Availlable'
                the_request.save()
            else:
                the_request.message = str(
                    the_request.quantity) + ' Requested ' + str(the_request.product.quantity) + ' Available'
                the_request.save()
                the_request.quantity = the_request.product.quantity
                the_request.save()
        all_request = Request.objects.filter(
            faculty=user, collected=False).all()
        check_record = Record.objects.filter(request__in=all_request)
        print(check_record)
        if check_record.exists():
            pass
        else:
            record = Record.objects.create()
            record.request.set(all_request)
            record.generate_random()
        return render(request, 'next.html', {"items": all_request})
    else:
        return render(request, 'nothing_selected.html')


def myrequest_status(request):
    user = request.user
    all_request = Request.objects.filter(faculty=user, collected=False).all()
    return render(request, 'request_status.html', {"request": all_request})


def generate_pdf(request, reprint=False):
    # Create a file-like buffer to receive PDF data.
    alert()  # check if any item's quantity is low and alert the admins
    user = request.user
    if reprint:
        check_record = get_object_or_404(Record, id=reprint)
        all_request = check_record.request.all()
    else:
        all_request = Request.objects.filter(
            faculty=user, collected=False).all()
        the_request = get_list_or_404(Request, faculty=user, collected=False)
        check_record = get_object_or_404(Record, request__id=the_request[0].id)
        for item in all_request:
            item.collected = True
            item.save()
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(120, 800, "KANO UNIVERSITY OF SCIENCE AND TECHNOLOGY,WUDIL")
    p.drawString(220, 780, "PROCUREMENT DEPARTMENT")
    p.drawString(170, 760, "AUTOMATED STORE MANAGEMENT SYSTEM")
    p.drawString(240, 740, "REQUISITION FORM")
    p.drawString(80, 720, "")
    p.drawString(380, 720, "    REQUEST NO: " + str(check_record.request_num))
    p.line(50, 715, 560, 715)
    p.drawString(50, 700, "S/N")
    p.drawString(100, 700, "REQUEST ITEM")
    p.drawString(300, 700, "AMOUNT")
    p.drawString(400, 700, "STATUS")
    p.line(50, 695, 560, 695)
    height_counter = 680
    counter = 1
    for item in all_request:
        p.drawString(50, height_counter, str(counter))
        p.drawString(100, height_counter, str(item.product.name))
        p.drawString(300, height_counter, str(item.quantity))
        p.drawString(400, height_counter, str(item.message))
        p.line(50, height_counter - 10, 560, height_counter - 10)
        height_counter -= 25
        counter += 1
    height_counter -= 3
    p.drawString(300, height_counter,
                 "*You will be notified of items that are out of stock")
    height_counter -= 25
    p.drawString(50, height_counter, "Faculty Name")
    p.line(130, height_counter, 500, height_counter)
    p.drawString(50, height_counter - 20, "Messenger Name")
    p.line(140, height_counter - 20, 500, height_counter - 20)
    p.drawString(50, height_counter - 40, "Sign & Date")
    p.drawString(350, height_counter - 40, "Approved By")
    p.line(120, height_counter - 80, 47, height_counter - 80)
    p.line(500, height_counter - 80, 350, height_counter - 80)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    check_record.printed = True
    check_record.save()
    print(item.faculty.faculty_name)
    print(item.faculty.faculty_name)
    print(item.faculty.faculty_name)
    print(item.faculty.faculty_name)
    print(item.faculty.faculty_name)
    filename = 'Requisition_Form' + ' Of ' + \
        str(item.faculty.faculty_name) + " " + '.pdf'
    print(filename)
    return FileResponse(buffer, as_attachment=True, filename=filename)


def alert():
    """Used to alert the admins  if a particular item is less than five"""
    admins = StoreUser.objects.filter(is_superuser=True)
    items = Item.objects.filter(quantity__lte=5)
    if items.exists():
        print("nayi karanci")
        for item in items:
            message = 'You  neeed to supply More ' + str(item.name)
            for admin in admins:
                return Notification.objects.create(text=message, faculty=admin)


def alert_faculty(item_id):
    item = Item.objects.filter(id=item_id)
    message = str(item.name) + \
        'Has now arrived  you can now order your remaining'
    Notification.objects.create(text='The')


def search(request):
    keyword = request.GET.get('search')
    results = Item.objects.filter(name__icontains=keyword)
    return render(request, 'results.html', {'results': results})


def index(request):
    return render(request, 'index.html')


def categories_list(request):
    alert()  # check if any item's quantity is low and alert the admins
    the_categories = Category.objects.all()
    return render(request, 'categories.html', {"categories": the_categories})


def categories_view(request, category_id):
    alert()  # check if any item's quantity is low and alert the admins
    items = get_list_or_404(Item, category__id=category_id, quantity__gt=0)
    # print(dir(the_category))
    # items = the_category.items.all()
    return render(request, 'request.html', {'items': items})


# jiegwwjgiojgwgoijwoi


# admin functionalities
class AddItemView(FormView):
    template_name = 'add_item.html'
    form_class = AddItemForm
    success_url = '/added_successfully.html'


def add_item(request):
    form = AddItemForm()
    if request.method == "POST":
        name = request.POST.get("name")
        print(name)
        quantity = request.POST.get("quantity")
        print(quantity)
        image = request.POST.get("image")
        print(image)
        restriction = request.POST.get("restriction")
        print(restriction)
        restriction_time = request.POST.get("restriction_time")
        print(restriction_time)
        my_category = request.POST.get("category")
        print(my_category)
        if name and quantity and image and restriction and restriction_time and my_category:
            category = get_object_or_404(Category, id=int(my_category))
            Item.objects.create(name=name, quantity=quantity, image=image,
                                restriction=restriction, restriction_time=restriction_time, category=category)
            return render(request, 'add_item.html', {"form": form})
        else:
            print("somthing isnt there")
    else:
        return render(request, 'add_item.html', {"form": form})


def add_category(request):
    form = AddCategoryForm()
    if request.method == "POST":
        form = AddCategoryForm(data=request.POST)
        name = request.POST.get("name")
        picture = request.POST.get("picture")
        print(picture)
        Category.objects.create(name=name, picture=picture)
        return render(request, 'add_category.html', {"form": form})
    else:
        return render(request, 'add_category.html', {"form": form})


def edit_item(request, item_id):
    user = request.user
    item = get_object_or_404(Item, id=item_id)
    form = AddItemForm(instance=item)
    if request.method == "POST":
        name = request.POST.get("name")
        quantity = request.POST.get("quantity")
        image = request.POST.get("image")
        restriction = request.POST.get("restriction")
        restriction_time = request.POST.get("restriction_time")
        category = request.POST.get("category")
        if name:
            item.name = name
        if quantity:
            item.quantity = quantity
        if image:
            item.iamge = image
        if restriction:
            item.restriction = restriction
        if restriction_time:
            item.restriction_time = restriction_time
        if category:
            category = get_object_or_404(Category, id=int(category))
            item.category = category
        item.save()
        return render(request, 'change_item.html', {"form": form})
    return render(request, "change_item.html", {"form": form})


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = AddCategoryForm(instance=category)
    if request.method == "POST":
        name = request.POST.get("name")
        picture = request.POST.get("picture")
        if name:
            category.name = name
        if picture:
            category.picture = picture
        category.save()
        form = AddCategoryForm(instance=category)
        return render(request, 'change_category.html', {"form": form})
    return render(request, "change_category.html", {"form": form})


def edit_user(request, user_id):
    user = get_object_or_404(StoreUser, id=user_id)
    form = ChangeUserForm(instance=user)
    if request.method == "POST":
        form = ChangeUserForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/store--admin")
    return render(request, "edit_user.html", {"form": form})


def add_user(request):
    form = ChangeUserForm()
    if request.method == "POST":
        form = ChangeUserForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/store-admin")
    return render(request, "add_user.html", {"form": form})


def change_item_list(request):
    items = Item.objects.all()
    return render(request, 'change_item_list.html', {"items": items})


def change_category_list(request):
    categories = Category.objects.all()
    return render(request, 'change_category_list.html', {"categories": categories})


class AddCategoryView(FormView):
    template_name = 'add_category.html'
    form_class = AddCategoryForm
    success_url = '/'


def store_admin(request):
    return render(request, 'admin.html')


def items_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {"items": items})

def users_list(request, change=False):
    users = StoreUser.objects.all()
    return render(request, 'users_list.html', {"users": users, "change": change})


def deactivate_user(request, user_id, activate=False):
    user = get_object_or_404(StoreUser, id=user_id)
    if activate:
        user.is_active = True
        user.save()
        the_return = after_deactivate_activate(request, True)
        return the_return
    else:
        user.is_active = False
        user.save()
        the_return = after_deactivate_activate(request, False)
        return the_return


def after_deactivate_activate(request, activate=False):
    if activate:
        return render(request, 'after_activate.html', {"activate": activate})
    else:
        return render(request, 'after_activate.html', {"activate": activate})
    pass


def admin_categories_list(request):
    categories = Category.objects.all()
    return render(request, 'categories_list.html', {"categories": categories})

def admin_notifications(request):
    notifs = Notification.objects.filter(faculty=request.user)
    return render(request, 'notification.html', {"notifs": notifs})


def faculty_records(request, faculty_id):
    user = get_object_or_404(StoreUser, id=faculty_id)
    all_request = Request.objects.filter(faculty=user).all()
    check_record = Record.objects.filter(
        request__in=all_request).order_by('-time')
    return render(request, 'users_record.html', {"records": check_record})


def records(request):
    users = StoreUser.objects.all()
    return render(request, 'records.html', {"users": users})
