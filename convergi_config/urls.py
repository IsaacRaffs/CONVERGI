from django.contrib import admin
from django.urls import path, include 
from core.views import listar_empresas, SearchView, Dashboard, home
from django.contrib.auth import views as auth
from user import views as user_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', admin.site.urls),
    
    path('', home, name='home'),
    path('dashboard/', Dashboard, name='dashboard'),
    path('empresas/', listar_empresas, name='empresas'),
    path('results/', SearchView.as_view(), name="search"),

    path('', include('user.urls')),
    path('logout/', auth.LogoutView.as_view(template_name ='user/index.html'), name ='logout'),
    path('register/', user_view.register, name ='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

