from django.urls import path
from .views import login_api, convidar_usuario_api, completar_cadastro_api

urlpatterns = [
    path('login/', login_api, name='login_api'),
    path('convidar/', convidar_usuario_api, name='convidar_usuario_api'),
    path('completar-cadastro/', completar_cadastro_api, name='completar_cadastro_api'),
]

