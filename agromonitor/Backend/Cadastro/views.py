import bcrypt
import json
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import Usuario, UsuarioConvite

# Número máximo de tentativas
MAX_TENTATIVAS = 5


def obter_usuario_autenticado(request):
    """Extrai o user_id da sessão ou headers"""
    user_id = request.session.get('user_id') or request.headers.get('X-User-ID')
    if user_id:
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return None
    return None


# =============================
# LOGIN
# =============================

@csrf_exempt
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
            user.ultimo_login = timezone.now()
            user.save(update_fields=['tentativas_falhas', 'ultimo_login'])
            request.session['user_id'] = user.id
            return JsonResponse({'message': 'Sucesso!', 'user_id': user.id}, status=200)

        user.tentativas_falhas += 1
        if user.tentativas_falhas >= MAX_TENTATIVAS:
            user.bloqueio = True
        user.save(update_fields=['tentativas_falhas', 'bloqueio'])
        return JsonResponse({'error': 'Senha incorreta.'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================
# CADASTRO (novo fluxo com convite)
# =============================

@csrf_exempt
@require_http_methods(["POST"])
def convidar_usuario_api(request):
    """Usuário logado convida outro usuário via email"""
    try:
        # Verifica autenticação
        usuario_logado = obter_usuario_autenticado(request)
        if not usuario_logado:
            return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

        data = json.loads(request.body.decode('utf-8'))
        usuario = data.get('usuario')
        email = data.get('email')
        role = data.get('role')

        if not usuario or not email or not role:
            return JsonResponse({'error': 'Usuário, email e role são obrigatórios.'}, status=400)

        if usuario_logado.role == 'owner':
            allowed_roles = ['supervisor', 'employee']
        elif usuario_logado.role in ['super_admin', 'admin']:
            allowed_roles = ['owner']
        else:
            return JsonResponse({'error': 'Você não tem permissão para enviar convites.'}, status=403)

        if role not in allowed_roles:
            return JsonResponse({'error': f'Role inválida. Usuários com role {usuario_logado.role} podem convidar apenas: {", ".join(allowed_roles)}.'}, status=400)

        # Validações
        if len(usuario) < 3 or len(usuario) > 15:
            return JsonResponse({'error': 'Usuário deve ter entre 3 e 15 caracteres.'}, status=400)

        if Usuario.objects.filter(usuario=usuario).exists():
            return JsonResponse({'error': 'Usuário já existe.'}, status=409)

        if Usuario.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email já cadastrado.'}, status=409)

        # Cria convite
        convite = UsuarioConvite.objects.create(
            usuario=usuario,
            email=email,
            role=role,
            criado_por=usuario_logado
        )

        # Envia email com link de cadastro
        link_cadastro = f"{settings.FRONTEND_URL}/completar-cadastro/{convite.token}"
        mensagem = f"""
Olá,

Você foi convidado para criar uma conta. Clique no link abaixo para completar seu cadastro:

{link_cadastro}

Este link expira em 7 dias.

Atenciosamente,
AgroMonitor
"""

        send_mail(
            subject='Convite para AgroMonitor',
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({
            'message': 'Convite enviado com sucesso!',
            'convite_id': convite.id
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def completar_cadastro_api(request):
    """Completa o cadastro usando o token do convite"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = data.get('token')
        senha = data.get('senha') or data.get('password')
        confirma_senha = data.get('confirma_senha') or data.get('confirmPassword')

        if not token or not senha or not confirma_senha:
            return JsonResponse({'error': 'Token e senha são obrigatórios.'}, status=400)

        if senha != confirma_senha:
            return JsonResponse({'error': 'As senhas não coincidem.'}, status=400)

        if len(senha) < 6:
            return JsonResponse({'error': 'A senha deve ter pelo menos 6 caracteres.'}, status=400)

        # Valida o convite
        convite = UsuarioConvite.objects.filter(token=token).first()
        if not convite:
            return JsonResponse({'error': 'Convite inválido.'}, status=404)

        if not convite.is_valido():
            return JsonResponse({'error': 'Convite expirado ou já utilizado.'}, status=410)

        # Criptografa senha
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
        email_hash = bcrypt.hashpw(convite.email.encode('utf-8'), salt).decode('utf-8')

        # Cria o usuário
        novo_usuario = Usuario.objects.create(
            usuario=convite.usuario,
            senha_hash=senha_hash,
            email=convite.email,
            email_hash=email_hash,
            role=convite.role
        )

        # Marca convite como utilizado
        convite.utilizado = True
        convite.usuario_criado = novo_usuario
        convite.save()

        return JsonResponse({
            'message': 'Cadastro realizado com sucesso!',
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


def Dashboard(request):
    return render(request, 'Dashboard.js')