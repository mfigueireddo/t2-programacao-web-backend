"""
Views (camada de API) do domínio de Usuários (Users).

Implementa os endpoints de autenticação própria do projeto e o gerenciamento
de usuários:

* ``SignupView`` — cadastra um usuário e já devolve um token de acesso.
* ``LoginView`` — autentica por nome e senha, retornando token e dados do usuário.
* ``LogoutView`` — invalida o token usado na requisição atual.
* ``MeView`` — consulta (``GET``) e atualiza parcialmente (``PATCH``) a conta do
  usuário logado; apenas administradores podem alterar o próprio papel.
* ``ChangePasswordView`` — troca a senha do usuário autenticado.
* ``ForgotPasswordView`` / ``ResetPasswordView`` — fluxo simplificado de
  recuperação de senha (o token é retornado na resposta, em vez de enviado por
  email).
* ``UserViewSet`` — leitura e atualização de usuários; a listagem é restrita a
  administradores e a alteração de papel só é permitida a administradores.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthToken, User
from .permissions import IsAdministrador, IsSelfOrAdministrador
from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    UserSerializer,
)


@extend_schema(request=SignupSerializer, responses=LoginResponseSerializer)
class SignupView(APIView):
    """Cria uma conta e já retorna token de acesso."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token = AuthToken.create_for_user(user)

        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(request=LoginSerializer, responses=LoginResponseSerializer)
class LoginView(APIView):
    """Autentica usuário por nome e senha."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = AuthToken.create_for_user(user)

        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            }
        )


class LogoutView(APIView):
    """Remove o token usado na requisição atual."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Consulta e altera a conta do usuário logado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)

        if request.user.role != User.Role.ADMINISTRADOR and 'role' in serializer.validated_data:
            return Response(
                {'role': 'Apenas administradores podem alterar permissões.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save()

        return Response(serializer.data)


@extend_schema(request=ChangePasswordSerializer)
class ChangePasswordView(APIView):
    """Troca a senha do usuário autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Senha alterada com sucesso. Faça login novamente.'}
        )


@extend_schema(request=ForgotPasswordSerializer)
class ForgotPasswordView(APIView):
    """Gera token para recuperação de senha e envia pelo console.

    Para simplificar o trabalho, o email é enviado usando o console backend
    do Django. Assim, a mensagem aparece no terminal do backend.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {
                'detail': (
                    'Email de recuperação enviado. '
                    'Verifique o terminal do backend para copiar o token.'
                )
            }
        )


@extend_schema(request=ResetPasswordSerializer)
class ResetPasswordView(APIView):
    """Redefine senha usando token de recuperação."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'Senha redefinida com sucesso.'})


@extend_schema_view(
    list=extend_schema(summary='Lista usuários'),
    retrieve=extend_schema(summary='Detalha usuário'),
    partial_update=extend_schema(summary='Atualiza usuário parcialmente'),
    update=extend_schema(summary='Atualiza usuário'),
)
class UserViewSet(viewsets.ModelViewSet):
    """Gerenciamento de usuários."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'put', 'head', 'options']

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdministrador()]

        if self.action in ('retrieve', 'partial_update', 'update'):
            return [permissions.IsAuthenticated(), IsSelfOrAdministrador()]

        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        request_user = self.request.user

        if request_user.role != User.Role.ADMINISTRADOR:
            serializer.validated_data.pop('role', None)

        serializer.save()