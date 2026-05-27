from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .models import Empresa, Contrato

from datetime import date, timedelta
import pandas as pd


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


@login_required
def importar_csv(request):
    resultado = None

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        arquivo = request.FILES.get('arquivo')

        if not arquivo:
            messages.error(request, 'Nenhum arquivo selecionado.')
            return redirect('importar')

        # tenta utf-8, cai para latin-1
        try:
            df = pd.read_csv(arquivo, encoding='utf-8')
        except UnicodeDecodeError:
            arquivo.seek(0)
            try:
                df = pd.read_csv(arquivo, encoding='latin-1')
            except Exception as e:
                messages.error(request, f'Erro ao ler o arquivo: {e}')
                return redirect('importar')
        except Exception as e:
            messages.error(request, f'Erro ao ler o arquivo: {e}')
            return redirect('importar')

        df.columns = df.columns.str.strip().str.lower()
        importados, ignorados, erros = 0, 0, []

        if tipo == 'empresas':
            obrigatorios = ['nome', 'inicio', 'termino', 'cidade']
            faltando = [c for c in obrigatorios if c not in df.columns]
            if faltando:
                messages.error(request, f'Colunas obrigatórias não encontradas: {", ".join(faltando)}')
                return redirect('importar')

            for i, row in df.iterrows():
                try:
                    nome = str(row.get('nome', '')).strip()
                    if not nome or nome.lower() == 'nan':
                        ignorados += 1
                        continue
                    if Empresa.objects.filter(nome__iexact=nome).exists():
                        ignorados += 1
                        continue
                    Empresa.objects.create(
                        nome=nome,
                        inicio=str(row.get('inicio', '')).strip(),
                        termino=str(row.get('termino', '')).strip(),
                        cidade=str(row.get('cidade', '')).strip(),
                        nome_fantasia=str(row.get('nome_fantasia', '')).strip() if pd.notna(row.get('nome_fantasia')) else '',
                        cnpj=str(row.get('cnpj', '')).strip() if pd.notna(row.get('cnpj')) else '',
                    )
                    importados += 1
                except Exception as e:
                    erros.append(f'Linha {i + 2}: {e}')

        elif tipo == 'contratos':
            obrigatorios = ['numero', 'tipo', 'objeto', 'fornecedor', 'responsavel', 'valor', 'data_inicio', 'data_fim']
            faltando = [c for c in obrigatorios if c not in df.columns]
            if faltando:
                messages.error(request, f'Colunas obrigatórias não encontradas: {", ".join(faltando)}')
                return redirect('importar')

            for i, row in df.iterrows():
                try:
                    numero = str(row.get('numero', '')).strip()
                    if not numero or numero.lower() == 'nan':
                        ignorados += 1
                        continue
                    if Contrato.objects.filter(numero__iexact=numero).exists():
                        ignorados += 1
                        continue

                    data_inicio = pd.to_datetime(row['data_inicio'], dayfirst=True).date()
                    data_fim = pd.to_datetime(row['data_fim'], dayfirst=True).date()

                    valor_str = str(row['valor']).strip().replace('.', '').replace(',', '.')
                    valor = float(valor_str)

                    tipo_val = str(row.get('tipo', 'CONTRATO')).strip().upper()
                    if tipo_val not in ['CONTRATO', 'CONVENIO']:
                        tipo_val = 'CONTRATO'

                    status_val = str(row.get('status', 'ATIVO')).strip().upper()
                    if status_val not in ['ATIVO', 'ENCERRADO', 'CANCELADO']:
                        status_val = 'ATIVO'

                    Contrato.objects.create(
                        numero=numero,
                        tipo=tipo_val,
                        objeto=str(row.get('objeto', '')).strip(),
                        fornecedor=str(row.get('fornecedor', '')).strip(),
                        responsavel=str(row.get('responsavel', '')).strip(),
                        valor=valor,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        status=status_val,
                    )
                    importados += 1
                except Exception as e:
                    erros.append(f'Linha {i + 2}: {e}')

        else:
            messages.error(request, 'Tipo de importação inválido.')
            return redirect('importar')

        resultado = {
            'tipo': 'Empresas' if tipo == 'empresas' else 'Contratos',
            'importados': importados,
            'ignorados': ignorados,
            'erros': erros,
        }

    return render(request, 'core/importar.html', {'resultado': resultado})