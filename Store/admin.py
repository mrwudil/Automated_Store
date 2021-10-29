from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import Item, Store, Request
from django.shortcuts import get_object_or_404

# Register your models here.


@register(Item)
class ItemAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(ItemAdmin, self).save_model(request, obj, form, change)
        stores = Store.objects.all()
        for store in stores:
            store.items.add(obj)

@register(Store)
class StoreAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if Store.objects.all().count() == 0:
            obj.id = 1
            super(StoreAdmin, self).save_model(request, obj, form, change)

admin.site.register(Request)