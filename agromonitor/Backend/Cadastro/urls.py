from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('src\components\Login', views.Login, name='Login'),
    path('src\components\Cadastro', views.Cadastro, name='Cadastro'),
    path('src\components\Recuparar', views.Recuperar, name='Recuperar'),
    #path('', views.estufas, name='estufas'),
    path('src\components\Dashboard', views.Dashboard, name='Dashboard'),
]


#ISSO DAQUI VAI VIRAR VIA !!API!!
#PEGAR OS NOMES DAS PAGS COM A GABI