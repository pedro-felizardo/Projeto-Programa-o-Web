from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sgea_app.urls')), # Inclui as URLs da aplicação principal
    path('api/', include('api.urls')) # URLs da API
]