from django.contrib import admin

# Register your models here.
from client.models import *

admin.site.register(AppSettings)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'snn', 'phone', 'gender')
    list_filter = ('firstName', 'lastName', 'snn',)
    search_fields = ('firstName', 'lastName', 'snn',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location', 'address', 'ID')


@admin.register(LoginUser)
class LoginUserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code')
    list_filter = ('phone', 'code')
    search_fields = ('phone', 'code')


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'snn', 'phone', 'barberName', 'point',)
    list_filter = ('firstName', 'lastName', 'snn',)
    search_fields = ('firstName', 'lastName', 'snn',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'barber', 'created_time', 'text',)
    list_filter = ('customer', 'barber', 'created_time', 'text',)
    search_fields = ('customer', 'barber', 'created_time', 'text',)


@admin.register(PresentedService)
class PresentedServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'barber', 'reserveTime', 'creationTime', 'status', 'payment', 'shift')
    list_filter = ('customer', 'barber', 'reserveTime', 'creationTime', 'status', 'payment', 'shift')
    search_fields = ('customer', 'barber', 'reserveTime', 'creationTime', 'status', 'payment', 'shift')

    def save_model(self, request, obj, form, change):
        id = PresentedService.objects.count()
        if obj.status == 'not paid':
            status = 1;
        obj.project_id = 'project_{}'.format(id + 1)
        obj.save()


@admin.register(SampleWork)
class SampleWorkAdmin(admin.ModelAdmin):
    list_display = ('barber', 'description',)
    list_filter = ('barber', 'description',)
    search_fields = ('barber', 'description',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('barber', 'cost',)
    list_filter = ('barber', 'cost',)
    search_fields = ('barber', 'cost',)


@admin.register(ServiceSchema)
class ServiceSchemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_schema_id', 'description', 'icon')
    list_filter = ('name', 'service_schema_id', 'description',)
    search_fields = ('name', 'service_schema_id', 'description',)
    exclude = ('service_schema_id',)

    def save_model(self, request, obj, form, change):
        id = ServiceSchema.objects.count()
        obj.service_schema_id = 'service_schema_{}'.format(id + 1)
        obj.save()


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('barber', 'week_days')
    list_filter = ('barber',)
    search_fields = ('barber',)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'shifts', 'workday', 'name')
    list_filter = ('name', 'start_time')
