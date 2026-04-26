from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Estufa(models.Model):
    nome = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)
    #usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome