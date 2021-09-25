from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Faculties(AbstractUser):
    avatar = models.ImageField()
    administrator = models.CharField(max_length=200)
    faculty_name =  models.CharField(max_length=500)
    phone = models.BigIntegerField(default=0)


class Notication(models.Model):
    text = models.TextField()
    faculty = models.ForeignKey(Faculties, on_delete=models.CASCADE)