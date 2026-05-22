from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocalidadeClimaViewSet, PrevisaoTempoViewSet, AlertaClimaViewSet,
    HistoricoClimaViewSet, clima_resumo_view, sincronizar_clima_view
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'localidades', LocalidadeClimaViewSet, basename='localidade')
router.register(r'previsoes', PrevisaoTempoViewSet, basename='previsao')
router.register(r'alertas', AlertaClimaViewSet, basename='alerta')
router.register(r'historicos', HistoricoClimaViewSet, basename='historico')

app_name = 'clima'

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Endpoints adicionais
    path('api/resumo/', clima_resumo_view, name='resumo'),
    path('api/sincronizar/', sincronizar_clima_view, name='sincronizar'),
]
