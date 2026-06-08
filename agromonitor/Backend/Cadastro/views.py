import bcrypt
import json
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse, FileResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from BD_FAZENDA.models import Estufa, RelatorioSensor
from .models import Usuario, UsuarioConvite, RecuperacaoSenha, UsuarioToken
import os
from datetime import datetime

# Número máximo de tentativas
MAX_TENTATIVAS = 5
# Rate limiting: máximo de 5 tentativas por IP em 15 minutos
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 900  # 15 minutos em segundos


def get_token_from_header(request):
    authorization = request.headers.get('Authorization', '')
    if authorization.startswith('Token '):
        return authorization.split(' ', 1)[1].strip()
    return None


def obter_usuario_autenticado(request):
    """Extrai o user_id da sessão, cabeçalho ou token de autenticação."""
    user_id = request.session.get('user_id') or request.headers.get('X-User-ID')
    if user_id:
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            pass

    token_key = get_token_from_header(request)
    if token_key:
        token = UsuarioToken.objects.filter(key=token_key).select_related('usuario').first()
        if token:
            return token.usuario

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
            
            # Criar token de autenticação exclusivo para o usuário
            UsuarioToken.objects.filter(usuario=user).delete()
            token = UsuarioToken.objects.create(usuario=user)

            response_role = 'admin' if user.role == 'super_admin' else user.role
            return JsonResponse({
                'message': 'Sucesso!',
                'user_id': user.id,
                'role': response_role,
                'is_super_admin': user.role == 'super_admin',
                'usuario': user.usuario,
                'token': token.key
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


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    """Desloga o usuário limpando sessao e tokens."""
    usuario_logado = obter_usuario_autenticado(request)
    if not usuario_logado:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    token_key = get_token_from_header(request)
    if token_key:
        UsuarioToken.objects.filter(key=token_key).delete()

    request.session.flush()

    return JsonResponse({'message': 'Logout realizado com sucesso.'}, status=200)


from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status as drf_status


@api_view(['GET', 'PATCH', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def perfil_api(request):
    """Retorna, atualiza ou exclui os dados do perfil do usuário autenticado.

    Implementado com Django REST Framework parsers para suportar `PATCH` com
    multipart/form-data corretamente (arquivos + campos).
    """
    # obter_usuario_autenticado espera um Django HttpRequest; DRF's request._request fornece isso
    django_request = getattr(request, '_request', request)
    usuario_logado = obter_usuario_autenticado(django_request)
    if not usuario_logado:
        return Response({'error': 'Usuário não autenticado.'}, status=drf_status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        response_role = 'admin' if usuario_logado.role == 'super_admin' else usuario_logado.role
        foto_url = None
        if usuario_logado.foto:
            foto_url = django_request.build_absolute_uri(usuario_logado.foto.url)
        return Response({
            'usuario': usuario_logado.usuario,
            'email': usuario_logado.email,
            'role': response_role,
            'is_super_admin': usuario_logado.role == 'super_admin',
            'foto_url': foto_url,
        }, status=drf_status.HTTP_200_OK)

    if request.method == 'DELETE':
        try:
            if getattr(usuario_logado, 'role', None) == 'super_admin' or getattr(usuario_logado, 'is_superuser', False):
                return Response({'error': 'Não é possível excluir o usuário super-admin.'}, status=drf_status.HTTP_403_FORBIDDEN)

            UsuarioToken.objects.filter(usuario=usuario_logado).delete()
            usuario_logado.delete()
            django_request.session.flush()
            return Response({'message': 'Conta excluída com sucesso.'}, status=drf_status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

    try:
        # Com DRF parsers, os dados vêm em request.data e arquivos em request.FILES
        novo_nome = request.data.get('nome') if 'nome' in request.data else None
        novo_email = request.data.get('email') if 'email' in request.data else None
        foto_file = request.FILES.get('foto') if hasattr(request, 'FILES') else None

        if novo_nome is None and novo_email is None and not foto_file:
            return Response({'error': 'Nenhum campo enviado para atualização.'}, status=drf_status.HTTP_400_BAD_REQUEST)

        update_fields = []

        if novo_nome is not None:
            novo_nome = str(novo_nome).strip()
            if not novo_nome:
                return Response({'error': 'Nome não pode ficar em branco.'}, status=drf_status.HTTP_400_BAD_REQUEST)
            if novo_nome != usuario_logado.usuario:
                if Usuario.objects.filter(usuario=novo_nome).exclude(pk=usuario_logado.pk).exists():
                    return Response({'error': 'Nome de usuário já está em uso.'}, status=drf_status.HTTP_409_CONFLICT)
                usuario_logado.usuario = novo_nome
                update_fields.append('usuario')

        if novo_email is not None:
            novo_email = str(novo_email).strip()
            if not novo_email:
                return Response({'error': 'E-mail não pode ficar em branco.'}, status=drf_status.HTTP_400_BAD_REQUEST)
            if novo_email != usuario_logado.email:
                if Usuario.objects.filter(email=novo_email).exclude(pk=usuario_logado.pk).exists():
                    return Response({'error': 'Email já cadastrado.'}, status=drf_status.HTTP_409_CONFLICT)
                usuario_logado.email = novo_email
                usuario_logado.email_hash = bcrypt.hashpw(novo_email.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_fields.extend(['email', 'email_hash'])

        if foto_file:
            usuario_logado.foto = foto_file
            update_fields.append('foto')

        if not update_fields:
            return Response({'message': 'Nenhuma alteração detectada.'}, status=drf_status.HTTP_200_OK)

        usuario_logado.save(update_fields=update_fields)
        response_role = 'admin' if usuario_logado.role == 'super_admin' else usuario_logado.role
        foto_url = None
        if usuario_logado.foto:
            foto_url = django_request.build_absolute_uri(usuario_logado.foto.url)

        return Response({
            'message': 'Perfil atualizado com sucesso.',
            'usuario': usuario_logado.usuario,
            'email': usuario_logado.email,
            'role': response_role,
            'foto_url': foto_url,
        }, status=drf_status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            role=convite.role,
            criado_por=convite.criado_por
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


def usuario_pode_acessar_estufa(usuario, estufa):
    if usuario.role == 'owner':
        return estufa.owner == usuario
    if usuario.role in ['supervisor', 'employee'] and usuario.criado_por:
        return estufa.owner == usuario.criado_por
    return False


@csrf_exempt
@require_http_methods(["GET", "POST"])
def estufas_api(request):
    """API para listar e cadastrar estufas."""
    try:
        usuario_logado = obter_usuario_autenticado(request)
        if not usuario_logado:
            return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

        if request.method == 'GET':
            if usuario_logado.role == 'owner':
                estufas_qs = Estufa.objects.filter(owner=usuario_logado)
            elif usuario_logado.role in ['supervisor', 'employee'] and usuario_logado.criado_por:
                estufas_qs = Estufa.objects.filter(owner=usuario_logado.criado_por)
            else:
                return JsonResponse({'estufas': []}, status=200)

            estufas = list(estufas_qs.values('id', 'nome', 'descricao'))
            return JsonResponse({'estufas': estufas}, status=200)

        if usuario_logado.role != 'owner':
            return JsonResponse({'error': 'Apenas owners podem cadastrar estufas.'}, status=403)

        data = json.loads(request.body.decode('utf-8'))
        nome = data.get('nome')
        descricao = data.get('descricao', '')

        if not nome:
            return JsonResponse({'error': 'Nome da estufa é obrigatório.'}, status=400)

        estufa = Estufa.objects.create(
            nome=nome,
            descricao=descricao,
            owner=usuario_logado
        )
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

@csrf_exempt
@require_http_methods(["GET"])
def relatorio_estufa_mensal_api(request, estufa_id):
    usuario_logado = obter_usuario_autenticado(request)
    if not usuario_logado:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    try:
        estufa = Estufa.objects.get(id=estufa_id)
    except Estufa.DoesNotExist:
        return JsonResponse({'error': 'Estufa não encontrada.'}, status=404)

    if not usuario_pode_acessar_estufa(usuario_logado, estufa):
        return JsonResponse({'error': 'Acesso negado a esta estufa.'}, status=403)

    mes_param = request.GET.get('mes')
    if mes_param:
        try:
            ano, mes = map(int, mes_param.split('-'))
        except ValueError:
            return JsonResponse({'error': 'Formato de mês inválido. Use YYYY-MM.'}, status=400)
    else:
        data_atual = timezone.now().date()
        ano, mes = data_atual.year, data_atual.month

    relatorio = RelatorioSensor.objects.filter(
        estufa=estufa,
        data_ultimo_relatorio__year=ano,
        data_ultimo_relatorio__month=mes
    ).order_by('-data_ultimo_relatorio').first()

    if not relatorio or not relatorio.arquivo_csv:
        return JsonResponse({
            'error': f'Nenhum relatório mensal encontrado para {ano}-{mes:02d}.'
        }, status=404)

    relatorio.arquivo_csv.open('rb')
    filename = os.path.basename(relatorio.arquivo_csv.name)
    response = FileResponse(relatorio.arquivo_csv, as_attachment=True, filename=filename)
    return response

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