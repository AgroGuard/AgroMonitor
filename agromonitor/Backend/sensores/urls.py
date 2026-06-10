from django.urls import path
from .views import (
    listar_dispositivos,
    enviar_comando_atuador,
    controlar_bomba,
    controlar_ventilador,
    historico_sensores,
    stats_sensores
)

urlpatterns = [
    # Dispositivos
    path('dispositivos/', listar_dispositivos, name='listar_dispositivos'),
    
    # Controle de atuadores
    path('comando/', enviar_comando_atuador, name='enviar_comando_atuador'),
    path('bomba/', controlar_bomba, name='controlar_bomba'),
    path('ventilador/', controlar_ventilador, name='controlar_ventilador'),
    
    # Histórico e estatísticas
    path('historico/', historico_sensores, name='historico_sensores'),
    path('stats/', stats_sensores, name='stats_sensores'),
]
