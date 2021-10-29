from django.db import models
from Users.models import StoreUser
# Create your models here.
RESTRICTION_TUPLE = (('1', 'Day'), (7, 'Week'), ('30', 'Month'), ('182', 'Half A Year'), ('365', 'Year'))



class Item(models.Model):
    name = models.TextField()
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='media/items/')
    restriction = models.PositiveSmallIntegerField()
    restriction_time = models.CharField(choices=RESTRICTION_TUPLE, max_length=20)


    def __str__(self):
        return str(self.name)

    def reduce_quantity(self, quantity):
        self.quantity -= quantity
        self.quantity.save()
        return True

    def add_quantity(self, quantity):
        self.quantity += quantity
        self.quantity.save()
        return True


class Store(models.Model):
    items = models.ManyToManyField(Item)

    def __str__(self):
        return str('KUST GENERAL STORE')


 
class Request(models.Model):
    product = models.ForeignKey(Item, related_name='product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    faculty = models.ForeignKey(StoreUser, on_delete=models.CASCADE, related_name='faculty')
    collected = models.BooleanField(default=False)
    message = models.TextField()

    def __str__(self) -> str:
        return str(f'{self.faculty} requested {self.product.name}')


    def record(self, u):
        pass

class Record(models.Model):
    request = models.ForeignKey(Request, on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now=True)
    alert = models.BooleanField(default=False)
    remaining = models.BooleanField(default=0)

    def __str__(self):
        return str(self.request.faculty.faculty_name) + 'collected' + str(self.request.quantity)  \
                            + str(self.request.product.name)

