from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .models import Empresa, Contrato

from datetime import date, timedelta
import csv
import io
from dateutil import parser as dateparser


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


def _ler_csv(arquivo):
    raw = arquivo.read()
    for encoding in ('utf-8-sig', 'utf-8', 'latin-1'):
        try:
            texto = raw.decode(encoding)
            reader = csv.DictReader(io.StringIO(texto))
            rows = list(reader)
            colunas = {k.strip().lower(): k for k in (reader.fieldnames or [])}
            return rows, colunas, None
        except UnicodeDecodeError:
            continue
    return None, None, 'Não foi possível decodificar o arquivo. Use UTF-8 ou Latin-1.'


def _parse_data(valor):
    return dateparser.parse(valor.strip(), dayfirst=True).date()


def _parse_valor(valor):
    v = valor.strip().replace(' ', '')
    if ',' in v and '.' in v:
        v = v.replace('.', '').replace(',', '.')
    elif ',' in v:
        v = v.replace(',', '.')
    return float(v)


@login_required
def importar_csv(request):
    resultado = None

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        arquivo = request.FILES.get('arquivo')

        if not arquivo:
            messages.error(request, 'Nenhum arquivo selecionado.')
            return redirect('importar')

        rows, colunas, erro = _ler_csv(arquivo)
        if erro:
            messages.error(request, erro)
            return redirect('importar')

        importados, ignorados, erros = 0, 0, []

        def col(row, nome):
            chave_original = colunas.get(nome)
            return row.get(chave_original, '').strip() if chave_original else ''

        if tipo == 'empresas':
            obrigatorios = ['nome', 'inicio', 'termino', 'cidade']
            faltando = [c for c in obrigatorios if c not in colunas]
            if faltando:
                messages.error(request, f'Colunas obrigatórias não encontradas: {", ".join(faltando)}')
                return redirect('importar')

            for i, row in enumerate(rows, start=2):
                try:
                    nome = col(row, 'nome')
                    if not nome:
                        ignorados += 1
                        continue
                    if Empresa.objects.filter(nome__iexact=nome).exists():
                        ignorados += 1
                        continue
                    Empresa.objects.create(
                        nome=nome,
                        inicio=col(row, 'inicio'),
                        termino=col(row, 'termino'),
                        cidade=col(row, 'cidade'),
                        nome_fantasia=col(row, 'nome_fantasia'),
                        cnpj=col(row, 'cnpj'),
                    )
                    importados += 1
                except Exception as e:
                    erros.append(f'Linha {i}: {e}')

        elif tipo == 'contratos':
            obrigatorios = ['numero', 'tipo', 'objeto', 'fornecedor', 'responsavel', 'valor', 'data_inicio', 'data_fim']
            faltando = [c for c in obrigatorios if c not in colunas]
            if faltando:
                messages.error(request, f'Colunas obrigatórias não encontradas: {", ".join(faltando)}')
                return redirect('importar')

            for i, row in enumerate(rows, start=2):
                try:
                    numero = col(row, 'numero')
                    if not numero:
                        ignorados += 1
                        continue
                    if Contrato.objects.filter(numero__iexact=numero).exists():
                        ignorados += 1
                        continue

                    tipo_val = col(row, 'tipo').upper()
                    if tipo_val not in ['CONTRATO', 'CONVENIO']:
                        tipo_val = 'CONTRATO'

                    status_val = col(row, 'status').upper()
                    if status_val not in ['ATIVO', 'ENCERRADO', 'CANCELADO']:
                        status_val = 'ATIVO'

                    Contrato.objects.create(
                        numero=numero,
                        tipo=tipo_val,
                        objeto=col(row, 'objeto'),
                        fornecedor=col(row, 'fornecedor'),
                        responsavel=col(row, 'responsavel'),
                        valor=_parse_valor(col(row, 'valor')),
                        data_inicio=_parse_data(col(row, 'data_inicio')),
                        data_fim=_parse_data(col(row, 'data_fim')),
                        status=status_val,
                    )
                    importados += 1
                except Exception as e:
                    erros.append(f'Linha {i}: {e}')

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