from django.urls import path
from .views import (
    login_api, 
    convidar_usuario_api, 
    completar_cadastro_api,
    estufas_api,
    solicitar_recuperacao_senha,
    confirmar_recuperacao_senha,
    validar_token_recuperacao
)

urlpatterns = [
    path('login/', login_api, name='login_api'),
    path('convidar/', convidar_usuario_api, name='convidar_usuario_api'),
    path('completar-cadastro/', completar_cadastro_api, name='completar_cadastro_api'),
    path('estufas/', estufas_api, name='estufas_api'),
    path('recuperar/solicitar/', solicitar_recuperacao_senha, name='solicitar_recuperacao_senha'),
    path('recuperar/confirmar/', confirmar_recuperacao_senha, name='confirmar_recuperacao_senha'),
    path('recuperar/validar/', validar_token_recuperacao, name='validar_token_recuperacao'),
]

