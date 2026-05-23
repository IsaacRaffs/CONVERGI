from django.contrib import admin
from .models import Empresa, Contrato

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["nome", "inicio", "termino", "cidade", "cnpj"]

@admin.register(Contrato)
class ConvenioaAdmin(admin.ModelAdmin):
    list_display = ["numero", "data_inicio", "data_fim", "fornecedor", "responsavel", "status"]
