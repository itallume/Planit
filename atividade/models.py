from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
import os

STATUS_CHOICES = [
    ("Pendente", "Pendente"),
    ("Concluído", "Concluído"),
    ("Atrasado", "Atrasado"),
]
class Atividade(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_paga = models.BooleanField(default=False)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    data_prevista = models.DateField()
    hora_prevista = models.TimeField()
    data_criacao = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pendente")
    ambiente = models.ForeignKey('ambiente.Ambiente', on_delete=models.CASCADE)
    descricao = models.TextField(blank=True, null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    responsaveis = models.ManyToManyField('auth.User', related_name='atividades_responsaveis', blank=True)
    participantes_alocados = models.ManyToManyField('ambiente.Participante', related_name='atividades_alocadas', blank=True)

    def __str__(self):
        return self.descricao[:50]
    
class Referencia(models.Model):
    tipo = models.CharField(max_length=100)
    nome_arquivo = models.CharField(max_length=200)
    arquivo = models.FileField(
        upload_to='referencias/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome_arquivo
    
    def save(self, *args, **kwargs):
        if self.arquivo:
            extensao = os.path.splitext(self.arquivo.name)[1].lower().strip('.')
            tipo_mapa = {
                'pdf': 'PDF',
                'jpg': 'Imagem JPG',
                'jpeg': 'Imagem JPEG',
                'png': 'Imagem PNG',
            }
            self.tipo = tipo_mapa.get(extensao, extensao.upper())
        super().save(*args, **kwargs)
    
class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    sobre = models.TextField()

    def __str__(self):
        return self.nome

class Endereco(models.Model):
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, related_name='enderecos')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, null=True, related_name='enderecos')

    def __str__(self):
        return f"{self.rua}, {self.cidade}"