from pyexpat.errors import messages
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from django.shortcuts import redirect, render
import bcrypt




# Número máximo de tentativas
MAX_TENTATIVAS = 5

# =============================
# LOGIN
# =============================
def Login(request):
    if request.method == 'POST':

        # Pegando dados do formulário
        email_ou_usuario = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario_bd = email_ou_usuario
        categoria_bd = 1

        try:
            #Busca usuário no banco
            user = Usuario.objects.get(usuario=usuario_bd, categoria=categoria_bd)
        except Usuario.DoesNotExist:
             #Se não encontrar
            messages.error(request, "Usuário não encontrado ou categoria incorreta.")
            return redirect('home')

        # Verifica se está bloqueado
        if user.bloqueio:
            messages.error(request, "Conta bloqueada devido a múltiplas tentativas.")
            return redirect('home')

        # Verifica senha com bcrypt
        if bcrypt.checkpw(senha.encode('utf-8'), user.senha_hash.encode('utf-8')):

            # Login correto → zera tentativas
            user.tentativas_falhas = 0
            user.save()

            return render(request, 'proximo.html')

        else:
            # Senha errada
            user.tentativas_falhas += 1

            if user.tentativas_falhas >= MAX_TENTATIVAS:
                # Bloqueia conta
                user.bloqueio = True
                messages.error(request, "🚫 Conta bloqueada após 5 tentativas.") #aqui devemos criar um pop-up apresentando essa mensagem
            else:
                restantes = MAX_TENTATIVAS - user.tentativas_falhas
                messages.warning(request, f"❌ Senha incorreta. Restantes: {restantes}") #aqui devemos criar um pop-up apresentando essa mensagem

            user.save()
            return redirect('home')

    return redirect('home')


# =============================
# CADASTRO
# =============================
def Cadastro(request):
    if request.method == 'POST':

        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma_senha')

        # Verifica senha
        if senha != confirma_senha:
            messages.error(request, "As senhas não coincidem.") # Essa mensagem aparece quando as duas senhas n coincidem, deixo pra vc descidir onde colocar ela
            return redirect('cadastro')

        # Criptografia com bcrypt
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
        email_hash = bcrypt.hashpw(email.encode('utf-8'), salt).decode('utf-8')

        try:
            # Cria usuário
            Usuario.objects.create(
                usuario=usuario,
                senha_hash=senha_hash,
                email_hash=email_hash,
                categoria=1
            )

            messages.success(request, "Usuário criado com sucesso!")# Gabi vc descide se quer q aparece um pop-up ou só uma mensagem em algum canto
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Erro: {e}")# Gabi vc descide se quer q aparece um pop-up ou só uma mensagem em algum canto
            return redirect('cadastro')

    return render(request, 'cadastro.html')


# =============================
# OUTRAS TELAS
# =============================
def Recuperar(request):
    return render(request, 'Recuperar.js')


#def estufa(request):
    #return render(request, 'estufa.html')


def Dashboard(request):
    return render(request, 'Dashboard.js')