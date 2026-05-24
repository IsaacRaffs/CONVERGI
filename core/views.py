from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from .models import Empresa, Contrato

from datetime import date, timedelta


# página que contém o sobre nós e o propósito
def home(request):
    return render(request, "core/home.html")


def listar_empresas(request, empresa_id=None):
        # pega todas as empresas e ordena elas pelo id
        all_empresas = Empresa.objects.all().order_by('id')
        p = Paginator(all_empresas, 5)
        page_number = request.GET.get('page')
        
        try:
            page_obj = p.get_page(page_number) 

        except PageNotAnInteger:
                page_obj = p.page(1)

        except EmptyPage:
                page_obj = p.page(p.num_pages)

        # compactar o conjunto de variáveis pro jinja 
        context = {
                'empresas': page_obj.object_list,
                'page_obj': page_obj
        }

        return render(request, "core/listar_empresas.html", context)

class SearchView(ListView):
    model = Empresa
    template_name = 'listar_empresas.html'
    context_object_name = 'empresas'
    paginate_by = 5

    # parametrização das queries
    def get_queryset(self):
        query = self.request.GET.get('search')
        if query:
            return Empresa.objects.filter(nome__icontains=query).order_by('id')
        return Empresa.objects.all().order_by('id')

def Dashboard(request):
    hoje = date.today()
    limite_30_dias = hoje + timedelta(days=30)

    # pega todos os contratos
    contratos = Contrato.objects.all()

    total_contratos = contratos.count()
    contratos_ativos = contratos.filter(status="ATIVO").count()
    contratos_vencidos = contratos.filter(data_fim__lt=hoje).count()

    # usando as variáveis de hoje e limite_30_d pra verificar os contratos vencidos
    contratos_vencendo_30 = contratos.filter(
        data_fim__gte=hoje,
        data_fim__lte=limite_30_dias
    ).count()

    valor_total = contratos.aggregate(
        total=Sum("valor")
    )["total"] or 0

    alertas_criticos = contratos.filter(
        status="ATIVO",
        data_fim__lte=limite_30_dias
    ).order_by("data_fim")[:10]

    # ordena usando a string e busca de trás pra frente em até 5 ocorrências
    ultimos_contratos = contratos.order_by("-criado_em")[:5]

    # faz a contagem dos contratos que estão com o nível de risco selecionado (em models)
    risco_alto = sum(1 for contrato in contratos if contrato.nivel_risco == "Alto")
    risco_medio = sum(1 for contrato in contratos if contrato.nivel_risco == "Médio")
    risco_baixo = sum(1 for contrato in contratos if contrato.nivel_risco == "Baixo")

    # compactar o conjunto de variáveis pro jinja 
    context = {
        "total_contratos": total_contratos,
        "contratos_ativos": contratos_ativos,
        "contratos_vencidos": contratos_vencidos,
        "contratos_vencendo_30": contratos_vencendo_30,
        "valor_total": valor_total,
        "alertas_criticos": alertas_criticos,
        "ultimos_contratos": ultimos_contratos,
        "risco_alto": risco_alto,
        "risco_medio": risco_medio,
        "risco_baixo": risco_baixo,
    }

    return render(request, "core/dashboard.html", context)