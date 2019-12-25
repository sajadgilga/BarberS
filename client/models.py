from django.db import models
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Customer(models.Model):
    ID = models.AutoField(primary_key=True, null=False, default=-1)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(to='Barber', related_name='customer')
    phone = models.CharField('contact phone', max_length=20)
    snn = models.CharField('national code', max_length=12)
    firstName = models.CharField('first name', max_length=20)
    lastName = models.CharField('last name', max_length=40)
    genderStatus = (
        ('f', 'female'),
        ('m', 'male')
    )
    gender = models.CharField(max_length=1, choices=genderStatus, default='m')
    credit = models.IntegerField(default=0)
    image = models.ImageField(upload_to='customers', null=True)
    location = models.CharField(max_length=200)
    isCompleted = models.BooleanField('', default=False)


class Location(models.Model):
    location = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=200, default='')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='location')
    chosen = models.BooleanField(default=False)
    ID = models.AutoField(primary_key=True)


class LoginUser(models.Model):
    code = models.CharField('verification code ', max_length=6)
    phone = models.CharField('logged in phone', max_length=12, unique=True)


class Barber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    phone = models.CharField('barber phone', max_length=20)
    snn = models.CharField('national code', max_length=12, default='')
    firstName = models.CharField('first name', max_length=20, default='')
    lastName = models.CharField('last name', max_length=40, default='')
    image = models.ImageField(null=True, upload_to='barbers')
    address = models.CharField('address', max_length=200, default='')
    location = models.CharField('location', max_length=200, default='')
    barberName = models.CharField(max_length=40, default='')
    point = models.FloatField(default=0)
    genderStatus = (
        ('f', 'female'),
        ('m', 'male')
    )
    gender = models.CharField(
        max_length=1,
        choices=genderStatus,
        default='m'
    )


class Comment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)

    created_time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()


class ServiceSchema(models.Model):
    name = models.CharField('service name', max_length=30)
    serviceId = models.IntegerField(primary_key=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='service-icons')  # is icon image?


class PresentedService(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    reserveTime = models.DateTimeField()
    creationTime = models.DateTimeField()

    status = models.CharField(max_length=20)
    payment = models.FloatField()
    shift = models.CharField(max_length=20)  # what is the type of shift


class SampleWork(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='barber_samples')


class WorkDay(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    morning_startTime = models.TimeField()
    morning_endTime = models.TimeField()
    afternoon_startTime = models.TimeField()
    afternoon_endTime = models.TimeField()


class Service(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    service = models.ForeignKey(to='ServiceSchema', on_delete=models.CASCADE)
    cost = models.FloatField('cost of service')

    class Meta:
        unique_together = (("barber", "service"),)
