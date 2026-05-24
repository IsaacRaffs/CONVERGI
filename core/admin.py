from django.contrib import admin
from .models import Empresa, Contrato
from import_export.admin import ImportExportActionModelAdmin

# registra a empresa no admin
@admin.register(Empresa)
class EmpresaAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ["nome", "inicio", "termino", "cidade", "cnpj"]
    list_filter = ["nome", "cidade", "inicio", "termino"] # gera uma busca para filtragem

# registra o convênio no admin
@admin.register(Contrato)
class ConvenioaAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ["numero", "data_inicio", "data_fim", "fornecedor", "responsavel", "status"]
    list_filter = ["numero", "data_inicio", "data_fim", "status"] # gera uma busca para filtragem