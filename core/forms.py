from django import forms
from .models import Contrato


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'numero', 'tipo', 'objeto', 'fornecedor',
            'responsavel', 'valor', 'data_inicio', 'data_fim', 'status',
        ]
        widgets = {
            'numero':      forms.TextInput(attrs={'class': 'form-control form-convergi', 'placeholder': 'Ex: 001/2024'}),
            'tipo':        forms.Select(attrs={'class': 'form-select form-convergi'}),
            'objeto':      forms.Textarea(attrs={'class': 'form-control form-convergi', 'rows': 3, 'placeholder': 'Descreva o objeto do contrato'}),
            'fornecedor':  forms.TextInput(attrs={'class': 'form-control form-convergi', 'placeholder': 'Nome do fornecedor / empresa'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control form-convergi', 'placeholder': 'Nome do responsável'}),
            'valor':       forms.NumberInput(attrs={'class': 'form-control form-convergi', 'placeholder': '0,00', 'step': '0.01'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control form-convergi', 'type': 'date'}),
            'data_fim':    forms.DateInput(attrs={'class': 'form-control form-convergi', 'type': 'date'}),
            'status':      forms.Select(attrs={'class': 'form-select form-convergi'}),
        }
        labels = {
            'numero':      'Número',
            'tipo':        'Tipo',
            'objeto':      'Objeto',
            'fornecedor':  'Fornecedor',
            'responsavel': 'Responsável',
            'valor':       'Valor (R$)',
            'data_inicio': 'Data de Início',
            'data_fim':    'Data de Término',
            'status':      'Status',
        }
