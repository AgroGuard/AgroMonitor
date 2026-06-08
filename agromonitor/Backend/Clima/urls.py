from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocalidadeClimaViewSet, PrevisaoTempoViewSet, AlertaClimaViewSet,
    HistoricoClimaViewSet, NotaUsuarioViewSet, clima_resumo_view,
    sincronizar_clima_view, cadastrar_regiao_view, listar_regioes_view,
    localidades_view, previsoes_atuais_compat_view,
    atualizar_previsao_compat_view, atualizar_todas_compat_view
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'localidades', LocalidadeClimaViewSet, basename='localidade')
router.register(r'previsoes', PrevisaoTempoViewSet, basename='previsao')
router.register(r'alertas', AlertaClimaViewSet, basename='alerta')
router.register(r'historicos', HistoricoClimaViewSet, basename='historico')
router.register(r'notes', NotaUsuarioViewSet, basename='nota')

app_name = 'clima'

urlpatterns = [
    # Compatibility routes: expose /api/localidades/ for clients expecting this path
    path('api/localidades/', localidades_view, name='localidades'),

    # Compatibility endpoints for root paths (allow unauthenticated access in DEBUG)
    path('api/localidades/<int:pk>/previsoes_atuais/', previsoes_atuais_compat_view, name='previsoes_atuais_compat'),
    path('api/localidades/<int:pk>/atualizar_previsao/', atualizar_previsao_compat_view, name='atualizar_previsao_compat'),
    path('api/localidades/atualizar_todas/', atualizar_todas_compat_view, name='atualizar_todas_compat'),

    # API REST
    path('api/', include(router.urls)),

    # Endpoints adicionais
    path('api/resumo/', clima_resumo_view, name='resumo'),
    path('api/sincronizar/', sincronizar_clima_view, name='sincronizar'),
    path('api/regioes/', listar_regioes_view, name='listar_regioes'),
    path('api/regioes/cadastrar/', cadastrar_regiao_view, name='cadastrar_regiao'),
    # Compatibility endpoints for root paths (allow unauthenticated access in DEBUG)
    path('api/localidades/<int:pk>/previsoes_atuais/', previsoes_atuais_compat_view, name='previsoes_atuais_compat'),
    path('api/localidades/<int:pk>/atualizar_previsao/', atualizar_previsao_compat_view, name='atualizar_previsao_compat'),
    path('api/localidades/atualizar_todas/', atualizar_todas_compat_view, name='atualizar_todas_compat'),
]
