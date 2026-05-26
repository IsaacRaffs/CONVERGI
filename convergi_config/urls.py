from django.contrib import admin
from django.urls import path, include
from core.views import listar_empresas, SearchView, Dashboard, home
from user import views as user_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('dashboard/', Dashboard, name='dashboard'),
    path('empresas/', listar_empresas, name='empresas'),
    path('results/', SearchView.as_view(), name='search'),

    path('register/', user_view.register, name='register'),
    path('', include('user.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
