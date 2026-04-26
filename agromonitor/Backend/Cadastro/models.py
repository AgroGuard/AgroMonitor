from django.db import models


class Usuario(models.Model):
    # Nome de usuário
    usuario = models.CharField(max_length=15, unique=True)

    # Senha criptografada
    senha_hash = models.CharField(max_length=255)

    # Email criptografado
    email_hash = models.CharField(max_length=255, unique=True)

    # Categoria 
    categoria = models.IntegerField(default=1)

    # Controle de tentativas
    tentativas_falhas = models.IntegerField(default=0)

    # Bloqueio da conta
    bloqueio = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario