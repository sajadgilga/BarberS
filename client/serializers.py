import re

from django.contrib.gis.geos import Point
from rest_framework import serializers

from BarberS.settings import generate_image_url
from barber.serializers import ServiceSerializer
from client.models import *


class CustomerSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['firstName', 'lastName', 'snn', 'gender', 'credit', 'image', 'email']

        # phone deleted !!!!!!!!!!!

    def create(self, validated_data):
        return Customer(**validated_data)

    def update(self, instance, validated_data):
        # instance.firstName = validated_data['firstName']
        # instance.lastName = validated_data['lastName']
        if 'name' not in validated_data:
            instance.name = validated_data['firstName'] + ' ' + validated_data['lastName']
        else:
            instance.name = validated_data['name']
        instance.snn = validated_data['snn']
        instance.gender = validated_data['gender']
        instance.image = validated_data['image']
        instance.email = validated_data['email']
        instance.save()
        return instance

    # def get_image(self, obj):
    #     try:
    #         return SERVER_BASE_URL + obj.image.url
    #     except:
    #         return ''


class LocationSerializer(serializers.ModelSerializer):
    customerID = serializers.CharField(source='customer.customer_id')

    class Meta:
        model = Location
        fields = ['address', 'customerID', 'ID', 'long', 'lat']
        read_only_fields = ['ID']

    def create(self, validated_data):
        customer = Customer.objects.filter(customer_id=validated_data.pop('customer')['customer_id']).first()
        location = Location(**validated_data, ID='location_{}'.format(Location.objects.count() + 1))
        location.customer = customer
        if len(customer.location.all()) == 0:
            location.chosen = True
        location.save()
        return location


class BarberSerializer(serializers.ModelSerializer):
    isTop = serializers.SerializerMethodField()

    class Meta:
        model = Barber
        fields = ['firstName', 'lastName', 'snn', 'gender', 'name', 'address', 'long', 'lat', 'image', 'barberName',
                  'point', 'isTop']
        read_only_fields = ['isTop']

    def get_isTop(self, obj):
        if obj.isTopBarber > 0:
            return True
        if obj.isTopBarber < 0:
            return False
        appSettings = AppSettings.load()
        return obj.point >= appSettings.threshold

    def update(self, instance, validated_data):
        try:
            # instance.firstName = validated_data['firstName']
            # instance.lastName = validated_data['lastName']
            if not validated_data['name']:
                instance.name = validated_data['firstName'] + ' ' + validated_data['lastName']
            else:
                instance.name = validated_data['name']
            instance.snn = validated_data['snn']
            instance.gender = validated_data['gender']
            instance.address = validated_data['address']
            instance.long = validated_data['long']
            instance.lat = validated_data['lat']
            # instance.locations = validated_data['location']
            instance.barberName = validated_data['barberName']
            instance.image = validated_data['image']
            instance.is_verified = True
            instance.save()
            return instance
        except:
            return instance


class BarberRecordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='barber_id')
    name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    isTop = serializers.SerializerMethodField()

    def get_name(self, obj):
        if not obj.name or obj.name == '':
            return '{} {}'.format(obj.firstName, obj.lastName)
        return obj.name

    def get_image_url(self, obj):
        try:

            return generate_image_url(obj)
        except:
            return ''

    def get_distance(self, obj):
        try:
            if not self.context['user_location']:
                return None
            user_long = self.context['user_location'].long
            user_lat = self.context['user_location'].lat
            barber_long = obj.long
            barber_lat = obj.lat
            # [user_long, user_lat] = self.context['user_location'].split(LOCATION_SEPARATOR)
            # [barber_long, barber_lat] = obj.location.split(LOCATION_SEPARATOR)
            p1 = Point(float(user_long), float(user_lat))
            p2 = Point(float(barber_long), float(barber_lat))
            d = p1.distance(p2)
            return d * 10 ** 5
        except:
            return None

    class Meta:
        model = Barber
        fields = ['id', 'name', 'image_url', 'distance', 'point', 'isTop']
        read_only_fields = ['id', 'name', 'image_url', 'distance', 'point', 'isTop']

    def get_isTop(self, obj):
        if obj.isTopBarber > 0:
            return True
        if obj.isTopBarber < 0:
            return False
        appSettings = AppSettings.load()
        return obj.point >= appSettings.threshold


class ServiceSchemaSerilzerIn(serializers.Serializer):
    serviceID_list = serializers.ListField(child=serializers.IntegerField())
    barber_username = serializers.CharField(max_length=150)


class PresentedServiceSerializer(serializers.ModelSerializer):
    barber_id = serializers.CharField(source='barber.barber_id')
    customer_id = serializers.CharField(source='customer.customer_id')
    service_id_list = serializers.SerializerMethodField()

    class Meta:
        model = PresentedService
        fields = ['barber_id', 'customer_id', 'service_id_list', 'reserveTime', 'status',
                  'payment',
                  'shift']

    def get_service_id_list(self, obj):
        all = obj.service.all()
        try:
            l = []
            for i in all:
                id = i.service_id
                l.append(id)
            return l
        except Exception as error:
            return error


class PresentedServiceSerializer_home(serializers.ModelSerializer):
    barber_id = serializers.CharField(source='barber.barber_id')
    customer_id = serializers.CharField(source='customer.customer_id')
    service_list = serializers.SerializerMethodField()
    barber_name = serializers.SerializerMethodField()
    barber_shop = serializers.SerializerMethodField()

    class Meta:
        model = PresentedService
        fields = ['barber_id', 'customer_id', 'service_list', 'reserveTime', 'status', 'barber_name',
                  'barber_shop',
                  'payment',
                  'shift']

    def get_barber_name(self, obj):
        # barber = Barber.objects.filter(barber_id = self.barber_id)
        barber = obj.barber

        # barber = Barber.objects.filter(barber_id =barber.barber_id).first()
        return barber.firstName + ' ' + barber.lastName

    def get_barber_shop(self, obj):
        barber = obj.barber
        # barber = Barber.objects.filter(barber_id = self.barber_id)

        # barber = Barber.objects.filter(barber=obj.barber).first()
        return barber.barberName

    def get_service_list(self, obj):
        service = obj.service.all()
        return ServiceSerializer(service, many=True).data


class PresentedServiceSerializer_in(serializers.ModelSerializer):
    barber_id = serializers.CharField(source='barber.barber_id')
    customer_id = serializers.CharField(source='customer.customer_id')
    service_id_list = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = PresentedService
        fields = ['barber_id', 'customer_id', 'service_id_list', 'reserveTime',
                  'payment',
                  'shift']

    def create(self, validated_data, barber, customer, status):
        project_id = 'project_{}'.format(PresentedService.objects.count() + 1)
        presented_service = PresentedService.objects.create(customer=customer, barber=barber,
                                                            reserveTime=validated_data['reserveTime'],
                                                            shift=validated_data['shift'],
                                                            status=status, project_id=project_id)
        # presented_service.save()  # todo :depends on  implemention maybe you need to delete this
        return presented_service

    # def get_service_id_list(self, obj):
    #     l = obj.service.all()
    #     try:
    #         list = []
    #         for i in l:
    #             temp = i.service_id
    #             list.add(temp)
    #         return list
    #     except:
    #         return None


#
# class ServiceSerializer(serializers.ModelSerializer):
#     service_schemaID = serializers.IntegerField(source='service.serviceId')
#     barber_id = serializers.CharField(source='barber.barber_id')
#
#     class Meta:
#         model = Service
#         fields = ['barber_id', 'service_schemaID', 'cost']
#
#     def create(self, validated_data):
#         try:
#             cost = validated_data['cost']
#             barber = Barber.objects.filter(barber_id=validated_data['barber']['barber_id']).first()
#             service = Customer.objects.filter(customer_id=validated_data['service']['serviceId']).first()
#         except:
#             return None
#         service_number = Service.count() + 1
#         service(cost=cost, barber=barber, service=service, service_number="service_{}".format(service_number))
#         service.save()


class BarberSerializer_out(serializers.ModelSerializer):
    sample_list = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    isTop = serializers.SerializerMethodField()

    class Meta:
        model = Barber
        fields = ['name', 'gender', 'address', 'point', 'long', 'lat', 'image', 'sample_list',
                  'barberName', 'services', 'isTop', 'barber_id']
        read_only_fields = ['isTop']

    def get_services(self, obj):
        services = Service.objects.filter(barber=obj)
        return ServiceSerializer(services, many=True).data

    def get_sample_list(self, obj):
        list = SampleWork.objects.filter(barber=obj)
        return SampleWorkSerializer(list, many=True).data

    def get_isTop(self, obj):
        if obj.isTopBarber > 0:
            return True
        if obj.isTopBarber < 0:
            return False
        appSettings = AppSettings.load()
        return obj.point >= appSettings.threshold


class CustomerSerializer_out(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    location = LocationSerializer(many=True)

    def get_image(self, obj):
        try:
            return generate_image_url(obj)
        except:
            return ''

    class Meta:
        model = Customer
        fields = ['name', 'snn', 'phone', 'gender', 'location', 'image', 'likes',
                  'customer_id']

    def get_likes(self, obj):
        list = obj.like.all()
        return BarberSerializer_out(list, many=True).data


class LeanCustomerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        try:
            return generate_image_url(obj)
        except:
            return ''

    class Meta:
        model = Customer
        fields = ['name', 'gender', 'image',
                  'customer_id']


class CommentSerializer(serializers.ModelSerializer):
    customer = LeanCustomerSerializer()
    barber_id = serializers.CharField(source='barber.barber_id')

    class Meta:
        model = Comment
        fields = ['customer', 'barber_id', 'text', 'created_time']
        read_only_fields = ['created_time', ]

    def create(self, validated_data):
        text = validated_data['text']

        try:
            barber_id = validated_data['barber']['barber_id']
            barber = Barber.objects.filter(barber_id=barber_id).first()
        except Exception as error:
            return None
        try:
            customer_id = validated_data['customer']['customer_id']
            customer = Customer.objects.filter(customer_id=customer_id).first()
        except Exception as error:
            print(error)
            return None
        if barber is None:
            return None

        comment = Comment.objects.create(customer=customer, barber=barber, text=text)
        comment.save()
        return comment


class bar_CommentSerializer(serializers.ModelSerializer):
    customer = LeanCustomerSerializer()
    barber_id = serializers.CharField(source='barber.barber_id')

    class Meta:
        model = Comment
        fields = ['customer', 'barber_id', 'text', 'created_time']


class SampleWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleWork
        fields = ['image']


class SampleWorkSerializer_in(serializers.ModelSerializer):
    barber_id = serializers.CharField(source='barber.barber_id')

    class Meta:
        model = SampleWork
        fields = ['image', 'description', 'barber_id']

    def create(self, validated_data):
        try:
            image = validated_data['image']
            description = validated_data['description']
            barber = Barber.objects.filter(barber_id=validated_data['barber']['barber_id']).first()
            sample = SampleWork(barber=barber, description=description, image=image)
            sample.save()
            return sample
        except:
            return None


class bar_BarberSerializer(serializers.ModelSerializer):
    service_list = serializers.SerializerMethodField()
    workday_list = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Barber
        # fields = '__all__'
        exclude = ['user', 'is_verified']

    def get_service_list(self, obj):
        service = Service.objects.filter(barber=obj)
        return ServiceSerializer(service, many=True).data

    def get_workday_list(self, obj):
        workdays = WorkDay.objects.filter(barber=obj)
        return WorkDaySerializer(workdays, many=True).data

    def get_image(self, obj):
        try:
            return generate_image_url(obj)
        except:
            return ''


class ShiftSerializer(serializers.ModelSerializer):
    barber_id = serializers.CharField(source='barber.barber_id')
    week_days = serializers.CharField(max_length=7, default='0000000')
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Shift
        fields = ['week_days', 'name', 'start_time', 'end_time', 'barber_id']
        # read_only_fields = ['barber_id']

    def create(self, validated_data):
        try:
            barber = Barber.objects.filter(barber_id=validated_data['barber']['barber_id']).first()
            week_days = validated_data['week_days']
            if self.week_days_validator(week_days) is None:
                return None
            workday = WorkDay(week_days=week_days, barber=barber)
            start_time = validated_data['start_time']
            end_time = validated_data['end_time']
            name = validated_data['name']

            workday.save()
            shift = Shift(workday=workday, start_time=start_time, end_time=end_time, name=name)
            shift.save()
            return shift
        except Exception as error:
            return None

    def week_days_validator(self, week_days):
        pattern = re.compile("[01]{7}")
        return re.match(pattern, week_days)


#
# class ServiceSerializer_out(serializers.ModelSerializer):
#     url = serializers.SerializerMethodField()
#     name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Service
#         fields = ['url', 'name', 'service_number']
#
#     def get_url(self, obj):
#         shema = obj.schema
#         return str(shema.icon)
#
#     def get_name(self, obj):
#         shema = obj.schema
#         return shema.name
#

# todo : make validator for another inputs especialy start_time and end_time

class WorkDaySerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = WorkDay
        fields = ['week_days', 'start_time', 'end_time']

    def get_start_time(self, obj):
        shift = Shift.objects.filter(workday=obj).first()
        return shift.start_time

    def get_end_time(self, obj):
        shift = Shift.objects.filter(workday=obj).first()
        return shift.end_time
