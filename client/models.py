import random

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from rest_framework.authtoken.models import Token

from BarberS.settings import SERVER_BASE_URL

client_image_fs = FileSystemStorage(location='static/images/customers', base_url=SERVER_BASE_URL)
barber_image_fs = FileSystemStorage(location='static/images/barbers', base_url=SERVER_BASE_URL)
service_image_fs = FileSystemStorage(location='static/images/services', base_url=SERVER_BASE_URL)
sample_image_fs = FileSystemStorage(location='static/images/samples', base_url=SERVER_BASE_URL)
tutorial_video_fs = FileSystemStorage(location='static/images/tutorial_videos',
                                      base_url='static/images/tutorial_videos')


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class AppSettings(SingletonModel):
    threshold = models.FloatField(default=4)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(to='Barber', related_name='customer')
    phone = models.CharField('contact phone', max_length=20)
    snn = models.CharField('national code', max_length=12)
    firstName = models.CharField('first name', max_length=20, default='')
    lastName = models.CharField('last name', max_length=40, default='')
    name = models.CharField('name', max_length=81, default='')
    email = models.EmailField('email', max_length=50)
    genderStatus = (
        ('f', 'female'),
        ('m', 'male')
    )
    gender = models.CharField(max_length=1, choices=genderStatus, default='m')
    credit = models.BigIntegerField(default=0)
    image = models.ImageField(null=True, storage=client_image_fs)
    # location = models.CharField(max_length=200)
    isCompleted = models.BooleanField('', default=True)
    customer_id = models.CharField(max_length=48)


class Location(models.Model):
    long = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=200, default='')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='location')
    chosen = models.BooleanField(default=False)
    ID = models.CharField(max_length=64, unique=True)


class LoginUser(models.Model):  # or login barber
    code = models.CharField('verification code ', max_length=6)
    phone = models.CharField('logged in phone', max_length=12, unique=True)
    # name = models.CharField(max_length=81, default='')
    # genderStatus = (
    #     ('f', 'female'),
    #     ('m', 'male')
    # )
    # gender = models.CharField(
    #     max_length=1,
    #     choices=genderStatus,
    #     default='m'
    # )


class Barber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    phone = models.CharField('barber phone', max_length=20)
    snn = models.CharField('national code', max_length=12, default='')
    firstName = models.CharField('first name', max_length=20, default='')
    lastName = models.CharField('last name', max_length=40, default='')
    name = models.CharField('name', max_length=81, default='')
    image = models.ImageField(null=True, storage=barber_image_fs)
    address = models.CharField('address', max_length=200, default='')
    location = models.CharField('location', max_length=200, default='')
    long = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    barberName = models.CharField(max_length=40, default='')
    point = models.FloatField(default=0)
    point_counter = models.BigIntegerField(default=0)
    genderStatus = (
        ('f', 'female'),
        ('m', 'male')
    )
    gender = models.CharField(
        max_length=1,
        choices=genderStatus,
        default='m'
    )
    barber_id = models.CharField(max_length=32, unique=True, default='barber_id_0')
    is_verified = models.BooleanField(default=True)

    BARBER_STATUS = (
        (-1, 'NOT_TOP'),
        (0, 'NEUTRAL'),
        (1, 'TOP'),
    )
    isTopBarber = models.IntegerField(default=0, choices=BARBER_STATUS)


class Comment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)

    created_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    text = models.TextField()


class ServiceSchema(models.Model):
    name = models.CharField('service name', max_length=30)
    service_schema_id = models.CharField(unique=True, max_length=32, default='service_schema_0')
    description = models.TextField()
    lower_limit = models.BigIntegerField(default=0)
    upper_limit = models.BigIntegerField(default=-1)
    icon = models.ImageField(storage=service_image_fs, null=True)  # is icon image?


def get_project_id():
    return 'project_{}'.format(random.randrange(1000, 10000, 1))
    # return datetime.datetime.now()


class PresentedService(models.Model):
    STATUS = (
        (1, 'UNVERIFIED'),
        (2, 'REJECTED'),
        (3, 'VERIFIED'),
        (4, 'DONE'),
    )
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    service = models.ManyToManyField(to='Service', related_name='presented_service')
    reserveTime = models.DateTimeField(null=True, blank=True)
    creationTime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    project_id = models.CharField(unique=True, default='project_0', max_length=32)

    status = models.BigIntegerField(choices=STATUS, default=1)
    payment = models.FloatField(default=-1)
    shift = models.CharField(max_length=20)  # what is the type of shift
    authority = models.CharField(max_length=60, default=-1)


class SampleWork(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(storage=sample_image_fs)


class WorkDay(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE)
    week_days = models.CharField(max_length=7, default='0000000')  # do not change the length of this !


class Shift(models.Model):
    shifts = (('m', 'morning'),
              ('a', 'afternoon')
              )
    name = models.CharField(max_length=30, choices=shifts, default='m')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    workday = models.ForeignKey('WorkDay', on_delete=models.CASCADE, related_name='shifts')


class Service(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE, related_name='services')
    schema = models.ForeignKey('ServiceSchema', on_delete=models.CASCADE, related_name='test')
    cost = models.FloatField('cost of service')
    service_id = models.CharField(unique=True, max_length=32, default='service_0')
    service_number = models.CharField(max_length=50, default='')
    enabled = models.BooleanField(default=True)


class TutorialVideo(models.Model):
    name = models.CharField(max_length=128, default='')
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    description = models.TextField(default='', blank=True)
    image = models.ImageField(storage=tutorial_video_fs)
    link = models.TextField(default='')
