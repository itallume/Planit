from django.db import models

# Create your models here.


class Ambiente(models.Model):

    nome = models.CharField(max_length=100)
    tema = models.CharField(max_length=100)

    def __str__(self):
        return self.nome