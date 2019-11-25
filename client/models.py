from django.db import models

class Costumer(models.Model):
    like = models.ManyToManyField('Barber')

    phone = models.CharField('contact phone',max_length = 20)
    snn = models.CharField('national code',max_length =12)#what is the maximum for snn
    firstName = models.CharField('first name',max_length = 20)
    lastName = models.CharField('last name',max_length = 40)

    genderStatus = (
        ('f','female'),
        ('m','male')
    )
    gender = models.CharField(
        max_length = 1,
        choices = genderStatus,
        default = 'm'

    )
    holding = models.IntegerField()#mojodi
    image = models.ImageField()
    location = models.CharField(max_length = 200);

class Barber(models.Model):
    phone = models.CharField('barber phone',max_length = 20);
    snn = models.CharField('national code', max_length=12)  # what is the maximum for snn
    firstName = models.CharField('first name', max_length=20)
    lastName = models.CharField('last name', max_length=40)
    image = models.ImageField()
    address = models.CharField('address',max_length = 200)
    location = models.CharField('location',max_length = 200)
    barberName = models.CharField(max_length = 40);
    point = models.FloatField()

class Comment (models.Model):
    dadan = models.ForeignKey('Costumer',on_delete=models.CASCADE)
    darbareYe = models.ForeignKey('Barber',on_delete=models.CASCADE)

    enterTime = models.DateTimeField(auto_now_add= True);
    text = models.TextField()

class Service(models.Model):
    name = models.CharField('service name',max_length=30)   ;
    serviceId = models.IntegerField();
    description = models.TextField();
    icon = models.ImageField()#is icon image?
class ProductedService(models.Model):
    get = models.ForeignKey('Barber',on_delete = models.CASCADE)
    eraeKhedmat=models.ForeignKey('Khedmat',on_delete = models.CASCADE)
    reserveTime = models.TimeField()
    creationTime = models.TimeField()

    status =models.CharField(max_length = 20)
    payment = models.FloatField()
    shift  =models.CharField(max_length = 20)# what is the type of shift

class SampleJob(models.Model):
    has = models.ForeignKey('Barber',on_delete =models.CASCADE)
    description = models.TextField()
    image = models.ImageField()
class WorkDay(models.Model):
    have = models.ForeignKey('Barber',on_delete =models.CASCADE)
    morning_startTime = models.TimeField()
    morning_endTime = models.TimeField()
    afternoon_startTime = models.TimeField()
    afternoon_endTime = models.TimeField()
class Khedmat(models.Model):
    erae = models.ForeignKey('Barber',on_delete =models.CASCADE)

    cost = models.FloatField('cost of service');

