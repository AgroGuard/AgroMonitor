from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions

from .models import UsuarioToken


class UsuarioTokenAuthentication(BaseAuthentication):
    """Autenticação DRF usando o token da tabela UsuarioToken."""

    keyword = 'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token_key = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')

        token = UsuarioToken.objects.select_related('usuario').filter(key=token_key).first()
        if token is None or token.usuario is None:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (token.usuario, token)

    def authenticate_header(self, request):
        return self.keyword
