from datetime import datetime
from random import randint, sample

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from client.models import Barber, Customer, Location, Comment, ServiceSchema, Service, Shift, WorkDay


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_samples(request):
    names = ['john', 'emilia', 'oxford', 'gholoom', 'ghobad', 'naseri', 'Lee']
    addresses = ['''9705 Court Dr.
Sebastian, FL 32958''', '''8098 Depot St.
Eastlake, OH 44095''', '''8376 Ramblewood Street
Utica, NY 13501''', '''8028 Berkshire St.
Ft Mitchell, KY 41017''', '''9232 Crescent Lane
Ossining, NY 10562''']
    locations = ['-13.23347 -- -118.56033', '-67.12578 -- 49.47014', '-30.32702 -- -41.06990', '102.78279 -- 35.99159',
                 '-67.12328 -- 49.42114', '-67.12574 -- 49.47024', '-67.12378 -- 49.47012', '-67.12378 -- 49.47022',
                 '-66.12372 -- 49.43015']
    barbers = create_barbers(names, addresses, locations)
    customers = create_customers(names, addresses)
    location_customers = create_locations(customers, locations, addresses)
    comments = create_comments(barbers, customers)
    schemas = create_service_schema()
    services = create_services(barbers, schemas)
    shifts = create_shifts(barbers)
    return Response()


def create_barbers(names, addresses, locations):
    BASE_USERNAME = 'barber'
    barbers = []
    try:
        for i in range(5):
            user = User.objects.create(username=BASE_USERNAME + '{}'.format(Barber.objects.count() + 1), password='password')
            barber = Barber()
            barber.user = user
            barber.barber_id = BASE_USERNAME + '_{}'.format(Barber.objects.count() + 1)
            barber.firstName = names[randint(0, 6)]
            barber.lastName = names[randint(0, 6)]
            barber.address = addresses[randint(0, len(addresses) - 1)]
            barber.location = locations[randint(0, len(locations) - 1)]
            barber.phone = '00000'
            barber.snn = '2-3904234'
            barber.is_verified = True
            barber.save()
            barbers.append(barber)
    except:
        return barbers
    return barbers


def create_locations(sample_customers, sample_locations, sample_addresses):
    BASE_USERNAME = 'location'
    locations = []
    used_customers = {}
    try:
        for i in range(5):
            location = Location()
            location.ID = BASE_USERNAME + '_{}'.format(Location.objects.count() + 1)
            location.address = sample_addresses[randint(0, len(sample_addresses) - 1)]
            location.location = sample_locations[randint(0, len(sample_locations) - 1)]
            customer = sample_customers[randint(0, len(sample_customers) - 1)]
            location.customer = customer
            if customer not in used_customers:
                used_customers[customer] = 1
                location.chosen = True
            location.save()
            locations.append(location)
    except:
        return locations
    return locations


def create_customers(names, addresses):
    BASE_USERNAME = 'customer'
    customers = []
    try:
        for i in range(5):
            user = User.objects.create(username=BASE_USERNAME + str(i), password='password')
            customer = Customer()
            customer.user = user
            customer.customer_id = BASE_USERNAME + '_{}'.format(Customer.objects.count() + 1)
            customer.firstName = names[randint(0, 6)]
            customer.lastName = names[randint(0, 6)]
            customer.email = 'abasi@abas.absdf'
            customer.address = addresses[randint(0, len(addresses) - 1)]
            customer.phone = '00000'
            customer.snn = '2-3904234'
            customer.isCompleted = True
            customer.save()
            customers.append(customer)
    except:
        return customers
    return customers


def create_comments(barbers, customers):
    comments = []
    try:
        for barber in barbers:
            comment = Comment()
            comment.barber = barber
            comment.customer = customers[randint(0, len(customers) - 1)]
            comment.text = 'comment text'
            comment.created_time = datetime.now()
            comment.save()
            comments.append(comment)
    except:
        return comments
    return comments


def create_service_schema():
    BASE = 'service_schema'
    schemas = []
    try:
        for i in range(10):
            schema = ServiceSchema()
            schema.service_schema_id = BASE + '_{}'.format(ServiceSchema.objects.count() + 1)
            schema.description = 'description text'
            schema.save()
            schemas.append(schema)
    except:
        return schemas
    return schemas


def create_services(barbers, schemas):
    BASE = 'service'
    services = []
    try:
        for barber in barbers:
            schema_samples = sample(schemas, randint(0, len(schemas) - 1))
            for schema in schema_samples:
                service = Service()
                service.barber = barber
                service.service_id = BASE + '_{}'.format(Service.objects.count() + 1)
                service.schema = schema
                service.cost = randint(0, 100) * 1000
                service.save()
                services.append(service)
    except:
        return services
    return services


def create_shifts(barbers):
    shifts = []
    try:
        for barber in barbers:
            shift = Shift()
            shift.name = Shift.shifts[randint(0, 1)]
            workday = WorkDay()
            workday.barber = barber
            workday.week_days = '0101110'
            workday.save()
            shift.workday = workday
            shift.save()
            shifts.append(shift)
    except:
        return shifts
    return shifts
