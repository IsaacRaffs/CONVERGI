from datetime import date
from django.db import models

# Classe empresa
class Empresa(models.Model):
    nome = models.CharField()
    inicio = models.CharField()
    termino = models.CharField()
    cidade = models.CharField()
    nome_fantasia = models.CharField(blank=True, default="")
    cnpj = models.CharField(blank=True)


    def __str__(self):
        return self.nome


# Classe Contrato 
class Contrato(models.Model):
    
    
    TIPO_CHOICES = [
        ("CONTRATO", "Contrato"),
        ("CONVENIO", "Convênio"),
    ]

    STATUS_CHOICES = [
        ("ATIVO", "Ativo"),
        ("ENCERRADO", "Encerrado"),
        ("CANCELADO", "Cancelado"),
    ]

    numero = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    objeto = models.TextField()
    fornecedor = models.CharField(max_length=150)
    responsavel = models.CharField(max_length=120)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ATIVO")
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    @property
    def dias_para_vencer(self):
        return (self.data_fim - date.today()).days

    @property
    def nivel_risco(self):
        dias = self.dias_para_vencer

        if dias < 0:
            return "Alto"
        if dias <= 15:
            return "Alto"
        if dias <= 30:
            return "Médio"
        return "Baixo"

    @property
    def esta_vencido(self):
        return self.dias_para_vencer < 0

    @property
    def vencendo_em_30_dias(self):
        return 0 <= self.dias_para_vencer <= 30

    def __str__(self):
        return f"{self.numero} - {self.fornecedor}"
