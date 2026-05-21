from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Usuario, UsuarioConvite, Estufa, RelatorioSensor
from django.utils import timezone
from datetime import timedelta
import uuid
import bcrypt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convidar_usuario_api(request):
    """API para convidar usuário (apenas owners podem convidar)"""
    usuario_atual = request.user

    if usuario_atual.role != 'owner':
        return Response({'error': 'Apenas owners podem convidar usuários'}, status=status.HTTP_403_FORBIDDEN)

    nome = request.data.get('nome')
    usuario = request.data.get('usuario')
    email = request.data.get('email')
    role = request.data.get('role')

    if not all([nome, usuario, email, role]):
        return Response({'error': 'Todos os campos são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

    if role not in ['supervisor', 'employee']:
        return Response({'error': 'Role inválido'}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(usuario=usuario).exists():
        return Response({'error': 'Nome de usuário já existe'}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(email=email).exists():
        return Response({'error': 'Email já cadastrado'}, status=status.HTTP_400_BAD_REQUEST)

    # Criar convite
    convite = UsuarioConvite.objects.create(
        nome=nome,
        usuario=usuario,
        email=email,
        role=role,
        criado_por=usuario_atual
    )

    # TODO: Enviar email com token de convite

    return Response({
        'message': 'Convite enviado com sucesso',
        'token': convite.token
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def completar_cadastro_api(request):
    """API para completar cadastro via convite"""
    token = request.data.get('token')
    senha = request.data.get('senha')

    if not all([token, senha]):
        return Response({'error': 'Token e senha são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

    convite = get_object_or_404(UsuarioConvite, token=token)

    if not convite.is_valido():
        return Response({'error': 'Convite inválido ou expirado'}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(usuario=convite.usuario).exists():
        return Response({'error': 'Usuário já existe'}, status=status.HTTP_400_BAD_REQUEST)

    # Criar hash da senha
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

    # Criar usuário
    novo_usuario = Usuario.objects.create(
        nome=convite.nome,
        usuario=convite.usuario,
        email=convite.email,
        role=convite.role,
        criado_por=convite.criado_por
    )

    # Marcar convite como utilizado
    convite.utilizado = True
    convite.usuario_criado = novo_usuario
    convite.save()

    return Response({
        'message': 'Cadastro completado com sucesso',
        'usuario': novo_usuario.usuario,
        'role': novo_usuario.role
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_api(request):
    """API para estatísticas da dashboard do tenant"""
    usuario_atual = request.user

    # Verificar se é owner ou supervisor
    if usuario_atual.role not in ['owner', 'supervisor']:
        return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)

    # Estatísticas básicas
    total_usuarios = Usuario.objects.filter(ativo=True).count()
    usuarios_ativos_hoje = Usuario.objects.filter(
        ultimo_login__date=timezone.now().date(),
        ativo=True
    ).count()

    # Estatísticas por role
    stats_por_role = Usuario.objects.filter(ativo=True).values('role').annotate(
        count=models.Count('id')
    )

    # Estufas
    total_estufas = Estufa.objects.count()

    return Response({
        'total_usuarios': total_usuarios,
        'usuarios_ativos_hoje': usuarios_ativos_hoje,
        'stats_por_role': list(stats_por_role),
        'total_estufas': total_estufas
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def estufas_api(request):
    if request.method == 'GET':
        estufas = Estufa.objects.all().values('id', 'nome', 'descricao')
        return Response({'estufas': list(estufas)}, status=status.HTTP_200_OK)

    # POST
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária.'}, status=status.HTTP_401_UNAUTHORIZED)

        nome = request.data.get('nome')
        descricao = request.data.get('descricao', '')

        if not nome:
            return Response({'error': 'Nome da estufa é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        estufa = Estufa.objects.create(nome=nome, descricao=descricao)
        return Response({
            'id': estufa.id,
            'nome': estufa.nome,
            'descricao': estufa.descricao
        }, status=status.HTTP_201_CREATED)