from django.db import models
from django.core.validators import RegexValidator

# Create your models here.


class Ambiente(models.Model):

    nome = models.CharField(max_length=100)
    tema = models.CharField(
        max_length=7, 
        blank=True,
        default='#F26800',
        validators=[
            RegexValidator(
                regex='^#[0-9A-Fa-f]{6}$',
                message='O tema deve ser uma cor no formato #RRGGBB (ex: #FF5733)',
            )
        ],
        help_text='Cor do tema no formato hexadecimal (ex: #FF5733)'
    )
    usuario_administrador = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    usuarios_participantes = models.ManyToManyField('auth.User', related_name='ambientes_participantes', blank=True)

    def __str__(self):
        return self.nome