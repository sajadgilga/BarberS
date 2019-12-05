from django.db import models
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(to='Barber', related_name='customer')

    isCompleted = models.BooleanField('', default=False)
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
    image = models.ImageField(null=True)
    location = models.CharField(max_length=200)


class Barber(models.Model):
    phone = models.CharField('barber phone', max_length=20)
    snn = models.CharField('national code', max_length=12)
    firstName = models.CharField('first name', max_length=20)
    lastName = models.CharField('last name', max_length=40)
    image = models.ImageField()
    address = models.CharField('address', max_length=200)
    location = models.CharField('location', max_length=200)
    barberName = models.CharField(max_length=40)
    point = models.FloatField()
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
    serviceId = models.IntegerField()
    description = models.TextField()
    icon = models.ImageField()  # is icon image?


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
    image = models.ImageField()


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


"""" automaticly make a token for new users"""

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)
