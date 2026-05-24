from django.contrib import admin
from django.urls import path, include
from core.views import listar_empresas, SearchView, dashboard, home

admin.site.site_header = "CONVERGI ADMIN"
admin.site.site_title = "Convergi ADM"  
admin.site.index_title = "Bem-vindo ao Painel de Controle do Convergi"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('empresas/', listar_empresas, name='empresas'),
    path('results/', SearchView.as_view(), name="search"),
]


