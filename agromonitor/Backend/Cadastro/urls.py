from django.urls import path
from .views import login_api, cadastro_api

urlpatterns = [
    path('login/', login_api, name='login_api'),
    path('cadastro/', cadastro_api, name='cadastro_api'),
]

