from django.db import models

class Usuarios(models.Model):
    id = models.BigAutoField
    usuario = models.CharField('usuario', max_length=100)
    telefone = models.IntegerField('telefone', max_length=11)
    cargo = models.CharField('cargo', max_length= 11)

    def __str__(self):
        return self.usuario

class Estufa(models.Model):
    id = models.BigAutoField
    nome = models.CharField('Nome', max_length=100)
    relatorio = models.FileField(upload_to='relatorio/')
    data =models.DateField(auto_now_add=True)
    def __str__(self):
        return self.nome