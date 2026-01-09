from django.db import models

# Create your models here.


class Ambiente(models.Model):

    nome = models.CharField(max_length=100)
    tema = models.CharField(max_length=100, blank=True, null=True)
    usuario_administrador = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    usuarios_participantes = models.ManyToManyField('auth.User', related_name='ambientes_participantes', blank=True)

    def __str__(self):
        return self.nome