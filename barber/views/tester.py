from datetime import datetime
from random import randint, sample

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

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


def create_barbers(names, addresses, locations):
    BASE_USERNAME = 'barber'
    barbers = []
    for i in range(5):
        user = User.objects.create(username=BASE_USERNAME + str(i), password='password')
        barber = Barber()
        barber.user = user
        barber.barber_id = BASE_USERNAME + '_{}'.format(Barber.objects.count() + 1)
        barber.firstName = names[randint(0, 6)]
        barber.lastName = names[randint(0, 6)]
        barber.address = addresses[randint(0, len(addresses))]
        barber.location = locations[randint(0, len(locations))]
        barber.phone = '00000'
        barber.snn = '2-3904234'
        barber.is_verified = True
        barber.save()
        barbers.append(barber)
    return barbers


def create_locations(sample_customers, sample_locations, sample_addresses):
    BASE_USERNAME = 'location'
    locations = []
    used_customers = {}
    for i in range(5):
        location = Location()
        location.ID = BASE_USERNAME + '_{}'.format(Location.objects.count() + 1)
        location.address = sample_addresses[randint(0, len(sample_addresses))]
        location.location = sample_locations[randint(0, len(sample_locations))]
        customer = sample_customers[randint(0, len(sample_customers))]
        location.customer = customer
        if customer not in used_customers:
            used_customers[customer] = 1
            location.chosen = True
        location.save()
        locations.append(location)
    return locations


def create_customers(names, addresses):
    BASE_USERNAME = 'customer'
    customers = []
    for i in range(5):
        user = User.objects.create(username=BASE_USERNAME + str(i), password='password')
        customer = Customer()
        customer.user = user
        customer.customer_id = BASE_USERNAME + '_{}'.format(Customer.objects.count() + 1)
        customer.firstName = names[randint(0, 6)]
        customer.lastName = names[randint(0, 6)]
        customer.email = 'abasi@abas.absdf'
        customer.address = addresses[randint(0, len(addresses))]
        customer.phone = '00000'
        customer.snn = '2-3904234'
        customer.isCompleted = True
        customer.save()
        customers.append(customer)
    return customers


def create_comments(barbers, customers):
    comments = []
    for barber in barbers:
        comment = Comment()
        comment.barber = barber
        comment.customer = customers[randint(0, len(customers))]
        comment.text = 'comment text'
        comment.created_time = datetime.now()
        comment.save()
        comments.append(comment)
    return comments


def create_service_schema():
    BASE = 'service_schema'
    schemas = []
    for i in range(10):
        schema = ServiceSchema()
        schema.service_schema_id = BASE + '_{}'.format(ServiceSchema.objects.count() + 1)
        schema.description = 'description text'
        schema.save()
        schemas.append(schema)
    return schemas


def create_services(barbers, schemas):
    BASE = 'service'
    services = []
    for barber in barbers:
        schema_samples = sample(schemas, randint(0, len(schemas)))
        for schema in schema_samples:
            service = Service()
            service.barber = barber
            service.service_id = BASE + '_{}'.format(Service.objects.count() + 1)
            service.schema = schema
            service.cost = randint(0, 100) * 1000
            service.save()
            services.append(service)
    return services


def create_shifts(barbers):
    shifts = []
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
    return shifts
