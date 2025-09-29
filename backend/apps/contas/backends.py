"""
Backends de autenticação customizados para o sistema.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailBackend(ModelBackend):
    """
    Backend de autenticação que permite login apenas com email.

    Este backend permite que os usuários façam login usando apenas o email,
    não o username. Isso é útil para sistemas onde o username é igual ao email
    mas queremos garantir que a autenticação seja sempre baseada no email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica um usuário usando email e senha.

        Args:
            request: HttpRequest object
            username: String que pode ser email ou username (tratamos como email)
            password: Senha do usuário
            **kwargs: Argumentos adicionais

        Returns:
            User object se autenticação bem sucedida, None caso contrário
        """
        if username is None or password is None:
            return None

        try:
            # Procura usuário pelo email (independente do username)
            # Normaliza o email para lowercase para busca case-insensitive
            email = username.lower().strip()

            # Busca usuário por email
            user = User.objects.get(email=email)

            # Verifica a senha
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        except User.DoesNotExist:
            # Executa hash da senha mesmo quando usuário não existe
            # para evitar timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários com mesmo email, retorna None
            # (isso não deveria acontecer com validação adequada)
            return None

        return None

    def get_user(self, user_id):
        """
        Obtém usuário pelo ID.

        Args:
            user_id: ID do usuário

        Returns:
            User object ou None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend de autenticação que permite login com email OU username.

    Este backend é mais flexível e permite login tanto com email quanto com username.
    Útil durante transições ou para compatibilidade com sistemas legados.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica um usuário usando email ou username com senha.

        Args:
            request: HttpRequest object
            username: String que pode ser email ou username
            password: Senha do usuário
            **kwargs: Argumentos adicionais

        Returns:
            User object se autenticação bem sucedida, None caso contrário
        """
        if username is None or password is None:
            return None

        try:
            # Normaliza entrada
            login_field = username.lower().strip()

            # Tenta encontrar usuário por email OU username
            user = User.objects.filter(Q(email__iexact=login_field) | Q(username__iexact=login_field)).first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user

        except Exception:
            # Em caso de erro, executa hash da senha para evitar timing attacks
            User().set_password(password)
            return None

        return None

    def get_user(self, user_id):
        """
        Obtém usuário pelo ID.

        Args:
            user_id: ID do usuário

        Returns:
            User object ou None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
