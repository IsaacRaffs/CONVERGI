from django.contrib import admin
from .models import Empresa, Contrato
from import_export.admin import ImportExportActionModelAdmin


@admin.register(Empresa)
class EmpresaAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ["nome", "inicio", "termino", "cidade", "cnpj"]

@admin.register(Contrato)
class ConvenioaAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ["numero", "data_inicio", "data_fim", "fornecedor", "responsavel", "status"]
