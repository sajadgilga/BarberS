from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from client.views.main_page import get_configs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path('barber/', include('barber.urls')),
    path('hateoas-config/', get_configs)
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
