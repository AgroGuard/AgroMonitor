import bcrypt
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Usuario

# Número máximo de tentativas
MAX_TENTATIVAS = 5

# =============================
# LOGIN
# =============================

@csrf_exempt  # Necessário para permitir chamadas do React sem o token CSRF do Django
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        identificador = data.get('email') or data.get('usuario')
        senha_digitada = data.get('password') or data.get('senha')

        if not identificador or not senha_digitada:
            return JsonResponse({'error': 'Email e senha são obrigatórios.'}, status=400)

        user = Usuario.objects.filter(email=identificador).first()
        if user is None:
            user = Usuario.objects.filter(usuario=identificador).first()

        if user is None:
            return JsonResponse({'error': 'Usuário não encontrado.'}, status=404)

        if user.bloqueio:
            return JsonResponse({'error': 'Conta bloqueada'}, status=403)

        if bcrypt.checkpw(senha_digitada.encode('utf-8'), user.senha_hash.encode('utf-8')):
            user.tentativas_falhas = 0
            user.save(update_fields=['tentativas_falhas'])
            return JsonResponse({'message': 'Sucesso!', 'user_id': user.id}, status=200)

        user.tentativas_falhas += 1
        if user.tentativas_falhas >= MAX_TENTATIVAS:
            user.bloqueio = True
        user.save(update_fields=['tentativas_falhas', 'bloqueio'])
        return JsonResponse({'error': 'Senha incorreta.'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# =============================
# CADASTRO
# =============================
@csrf_exempt
def cadastro_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))

        usuario = data.get('usuario') or data.get('nomeFuncionario')
        email = data.get('email')
        senha = data.get('senha') or data.get('password')
        confirma_senha = data.get('confirma_senha') or data.get('confirmPassword')

        # Validações básicas
        if not usuario or not email or not senha or not confirma_senha:
            return JsonResponse({'error': 'Todos os campos são obrigatórios.'}, status=400)

        if senha != confirma_senha:
            return JsonResponse({'error': 'As senhas não coincidem.'}, status=400)

        if len(senha) < 6:
            return JsonResponse({'error': 'A senha deve ter pelo menos 6 caracteres.'}, status=400)

        # Verifica se usuário já existe
        if Usuario.objects.filter(usuario=usuario).exists():
            return JsonResponse({'error': 'Usuário já existe.'}, status=409)

        if Usuario.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email já cadastrado.'}, status=409)

        # Criptografia com bcrypt
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
        email_hash = bcrypt.hashpw(email.encode('utf-8'), salt).decode('utf-8')

        # Cria usuário
        novo_usuario = Usuario.objects.create(
            usuario=usuario,
            senha_hash=senha_hash,
            email=email,
            email_hash=email_hash,
            categoria=1
        )

        return JsonResponse({
            'message': 'Usuário criado com sucesso!',
            'user_id': novo_usuario.id,
            'usuario': novo_usuario.usuario
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================
# OUTRAS TELAS
# =============================
def Recuperar(request):
    return render(request, 'Recuperar.js')


#def estufa(request):
    #return render(request, 'estufa.html')


def Dashboard(request):
    return render(request, 'Dashboard.js')