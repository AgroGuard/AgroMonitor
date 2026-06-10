from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from Clima.views import listar_regioes_view, localidades_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Cadastro.urls')),
    path('api/sensores/', include('sensores.urls')),
    path('api/localidades/', localidades_view),
    path('api/regioes/', listar_regioes_view),
    path('api/clima/', include('Clima.urls')),
    # Expose Clima app routes at project root so compatibility endpoints
    # that rely on /api/localidades/<id>/... work without the extra /clima/ prefix
    path('', include('Clima.urls')),
    path('dashboard/', include('Monitor.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
