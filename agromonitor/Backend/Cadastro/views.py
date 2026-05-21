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
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from BD_FAZENDA.models import Estufa
from .models import Usuario, UsuarioConvite, RecuperacaoSenha

# Número máximo de tentativas
MAX_TENTATIVAS = 5
# Rate limiting: máximo de 5 tentativas por IP em 15 minutos
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 900  # 15 minutos em segundos


def obter_usuario_autenticado(request):
    """Extrai o user_id da sessão ou headers"""
    user_id = request.session.get('user_id') or request.headers.get('X-User-ID')
    if user_id:
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return None
    return None


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def check_rate_limit(request, identificador):
    """Verifica rate limiting por IP e identificador"""
    client_ip = get_client_ip(request)
    cache_key = f"login_attempts_{client_ip}_{identificador}"
    
    attempts = cache.get(cache_key, 0)
    if attempts >= RATE_LIMIT_ATTEMPTS:
        return False, f"Muitas tentativas de login. Tente novamente em 15 minutos."
    
    return True, None


def increment_rate_limit(request, identificador):
    """Incrementa contador de tentativas de login"""
    client_ip = get_client_ip(request)
    cache_key = f"login_attempts_{client_ip}_{identificador}"
    
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, RATE_LIMIT_WINDOW)


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

        # Verificar rate limiting
        is_allowed, error_msg = check_rate_limit(request, identificador)
        if not is_allowed:
            return JsonResponse({'error': error_msg}, status=429)

        # Buscar usuário (não revelar se existe)
        user = Usuario.objects.filter(email=identificador).first()
        if user is None:
            user = Usuario.objects.filter(usuario=identificador).first()

        if user is None:
            increment_rate_limit(request, identificador)
            # Não revelar se usuário não existe (segurança)
            return JsonResponse({'error': 'Credenciais inválidas.'}, status=401)

        if user.bloqueio:
            return JsonResponse({'error': 'Conta bloqueada. Contate o administrador.'}, status=403)

        # Verificar senha
        if bcrypt.checkpw(senha_digitada.encode('utf-8'), user.senha_hash.encode('utf-8')):
            # Login bem-sucedido
            user.tentativas_falhas = 0
            user.ultimo_login = timezone.now()
            user.save(update_fields=['tentativas_falhas', 'ultimo_login'])
            request.session['user_id'] = user.id
            request.session.set_expiry(3600)  # Sessão expira em 1 hora
            
            # Limpar rate limit
            client_ip = get_client_ip(request)
            cache_key = f"login_attempts_{client_ip}_{identificador}"
            cache.delete(cache_key)
            
            response_role = 'admin' if user.role == 'super_admin' else user.role
            return JsonResponse({
                'message': 'Sucesso!',
                'user_id': user.id,
                'role': response_role,
                'usuario': user.usuario
            }, status=200)

        # Senha incorreta
        user.tentativas_falhas += 1
        if user.tentativas_falhas >= MAX_TENTATIVAS:
            user.bloqueio = True
        user.save(update_fields=['tentativas_falhas', 'bloqueio'])
        increment_rate_limit(request, identificador)
        
        return JsonResponse({'error': 'Credenciais inválidas.'}, status=401)

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

    Este link expira em 30 dias.

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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def estufas_api(request):
    """API para listar e cadastrar estufas."""
    try:
        usuario_logado = obter_usuario_autenticado(request)
        if not usuario_logado:
            return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

        if request.method == 'GET':
            estufas = list(Estufa.objects.all().values('id', 'nome', 'descricao'))
            return JsonResponse({'estufas': estufas}, status=200)

        data = json.loads(request.body.decode('utf-8'))
        nome = data.get('nome')
        descricao = data.get('descricao', '')

        if not nome:
            return JsonResponse({'error': 'Nome da estufa é obrigatório.'}, status=400)

        estufa = Estufa.objects.create(nome=nome, descricao=descricao)
        return JsonResponse({
            'message': 'Estufa cadastrada com sucesso!',
            'estufa': {
                'id': estufa.id,
                'nome': estufa.nome,
                'descricao': estufa.descricao
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================
# RECUPERAÇÃO DE SENHA
# =============================

@csrf_exempt
@require_http_methods(["POST"])
def solicitar_recuperacao_senha(request):
    """Solicita recuperação de senha via email"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email') or data.get('usuario')

        if not email:
            return JsonResponse({'error': 'Email ou usuário é obrigatório.'}, status=400)

        # Buscar usuário
        user = Usuario.objects.filter(email=email).first()
        if user is None:
            user = Usuario.objects.filter(usuario=email).first()

        if not user:
            # Não revelar se usuário existe (segurança)
            return JsonResponse({
                'message': 'Se o email existir em nossa base, você receberá um link de recuperação.'
            }, status=200)

        if user.bloqueio:
            return JsonResponse({
                'error': 'Sua conta está bloqueada. Entre em contato com o administrador.'
            }, status=403)

        # Limpar tokens antigos não utilizados
        RecuperacaoSenha.objects.filter(usuario=user, utilizado=False).delete()

        # Criar novo token de recuperação
        recuperacao = RecuperacaoSenha.objects.create(
            usuario=user,
            email=user.email
        )

        # Enviar email com link de recuperação
        link_recuperacao = f"{settings.FRONTEND_URL}/recuperar/{recuperacao.token}"
        mensagem = f"""
Olá {user.usuario},

Você solicitou a recuperação de sua senha. Clique no link abaixo para criar uma nova senha:

{link_recuperacao}

Este link expira em 1 hora.

Se você não solicitou esta recuperação, ignore este email.

Atenciosamente,
AgroMonitor
"""

        try:
            send_mail(
                subject='Recuperação de Senha - AgroMonitor',
                message=mensagem,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as email_error:
            # Log do erro, mas não revelar ao usuário
            print(f"Erro ao enviar email: {email_error}")

        return JsonResponse({
            'message': 'Se o email existir em nossa base, você receberá um link de recuperação.'
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def confirmar_recuperacao_senha(request):
    """Confirma recuperação de senha com novo token"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = data.get('token')
        nova_senha = data.get('nova_senha') or data.get('password')
        confirma_senha = data.get('confirma_senha') or data.get('confirmPassword')

        if not token or not nova_senha or not confirma_senha:
            return JsonResponse({'error': 'Token e senha são obrigatórios.'}, status=400)

        if nova_senha != confirma_senha:
            return JsonResponse({'error': 'As senhas não coincidem.'}, status=400)

        if len(nova_senha) < 6:
            return JsonResponse({'error': 'A senha deve ter pelo menos 6 caracteres.'}, status=400)

        if len(nova_senha) > 50:
            return JsonResponse({'error': 'A senha é muito longa.'}, status=400)

        # Validar token
        recuperacao = RecuperacaoSenha.objects.filter(token=token).first()
        if not recuperacao:
            return JsonResponse({'error': 'Link inválido.'}, status=404)

        if not recuperacao.is_valido():
            return JsonResponse({'error': 'Link expirado ou já utilizado.'}, status=410)

        # Atualizar senha
        user = recuperacao.usuario
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), salt).decode('utf-8')

        user.senha_hash = senha_hash
        user.tentativas_falhas = 0  # Resetar tentativas falhas
        user.bloqueio = False  # Desbloquear conta se estava bloqueada
        user.save(update_fields=['senha_hash', 'tentativas_falhas', 'bloqueio'])

        # Marcar recuperação como utilizada
        recuperacao.marcar_como_utilizado()

        return JsonResponse({
            'message': 'Senha alterada com sucesso!',
            'usuario': user.usuario
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def validar_token_recuperacao(request):
    """Valida se um token de recuperação é válido"""
    try:
        token = request.GET.get('token')

        if not token:
            return JsonResponse({'error': 'Token é obrigatório.'}, status=400)

        recuperacao = RecuperacaoSenha.objects.filter(token=token).first()
        if not recuperacao:
            return JsonResponse({'valid': False, 'error': 'Link inválido.'}, status=404)

        if not recuperacao.is_valido():
            return JsonResponse({'valid': False, 'error': 'Link expirado.'}, status=410)

        return JsonResponse({
            'valid': True,
            'usuario': recuperacao.usuario.usuario,
            'email': recuperacao.usuario.email,
            'tempo_expiracao': recuperacao.expira_em.isoformat()
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def Recuperar(request):
    return render(request, 'Recuperar.js')


def Dashboard(request):
    return render(request, 'Dashboard.js')