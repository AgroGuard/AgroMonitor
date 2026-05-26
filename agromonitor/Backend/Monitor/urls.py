from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/alertas/', views.listar_alertas, name='listar_alertas'),
    path('api/alertas/resolver/', views.resolver_alerta, name='resolver_alerta'),
]