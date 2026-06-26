"""
Views (camada de API) do domínio de Usuários (Users).

Implementa os endpoints de autenticação própria do projeto e o gerenciamento
de usuários:

* ``SignupView`` — cadastra um usuário e já devolve um token de acesso.
* ``LoginView`` — autentica por nome e senha, retornando token e dados do usuário.
* ``LogoutView`` — invalida o token usado na requisição atual.
* ``MeView`` — consulta (``GET``), atualiza parcialmente (``PATCH``) e exclui
  (``DELETE``) a conta do usuário logado; apenas administradores podem alterar
  o próprio papel.
* ``ChangePasswordView`` — troca a senha do usuário autenticado.
* ``ForgotPasswordView`` / ``ResetPasswordView`` — fluxo de recuperação de
  senha por token enviado ao email do usuário (entregue pelo console backend
  do Django durante o desenvolvimento).
* ``UserViewSet`` — leitura, atualização e exclusão de usuários; a listagem é
  restrita a administradores, a alteração de papel só é permitida a
  administradores e a exclusão é restrita ao próprio usuário ou a um
  administrador.
"""

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import permissions, serializers, status, viewsets
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


def _detail_response(description):
    """Resposta de schema com um único campo ``detail`` (mensagem de texto)."""
    return OpenApiResponse(
        response=inline_serializer(
            name=f'Detail{description.replace(" ", "")}',
            fields={'detail': serializers.CharField()},
        ),
        description=description,
    )


@extend_schema(
    summary='Cadastra um usuário',
    description=(
        'Cria uma conta e já devolve um token de acesso. "name" e "email" devem '
        'ser únicos e a senha precisa ter no mínimo 8 caracteres. O campo "role" é '
        'opcional (padrão USUARIO).'
    ),
    request=SignupSerializer,
    responses=LoginResponseSerializer,
    examples=[
        OpenApiExample(
            'Cadastro de usuário',
            value={
                'name': 'maria',
                'email': 'maria@exemplo.com',
                'password': 'senha-segura-123',
                'role': 'ADMINISTRADOR',
            },
            request_only=True,
        ),
    ],
)
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


@extend_schema(
    summary='Autentica um usuário',
    description='Autentica por nome e senha, retornando um token de acesso e os dados do usuário.',
    request=LoginSerializer,
    responses=LoginResponseSerializer,
    examples=[
        OpenApiExample(
            'Login',
            value={'name': 'maria', 'password': 'senha-segura-123'},
            request_only=True,
        ),
    ],
)
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


@extend_schema(
    summary='Encerra a sessão',
    description=(
        'Remove o token usado na requisição atual, invalidando-o. Requer estar '
        'autenticado (envie o token no cabeçalho Authorization).'
    ),
    request=None,
    responses={204: OpenApiResponse(description='Logout efetuado.')},
)
class LogoutView(APIView):
    """Remove o token usado na requisição atual."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary='Consulta a própria conta',
        description='Retorna os dados do usuário autenticado.',
        responses=UserSerializer,
    ),
    patch=extend_schema(
        summary='Atualiza a própria conta',
        description=(
            'Atualiza parcialmente os dados do usuário autenticado. Apenas '
            'administradores podem alterar o próprio papel ("role").'
        ),
        request=UserSerializer,
        responses=UserSerializer,
        examples=[
            OpenApiExample(
                'Atualizar email',
                value={'email': 'novo-email@exemplo.com'},
                request_only=True,
            ),
        ],
    ),
    delete=extend_schema(
        summary='Exclui a própria conta',
        description=(
            'Exclui a conta do usuário autenticado. As tarefas criadas têm o nome '
            'do criador preservado como "[DELETADO]" e as referências de criador/'
            'responsável são anuladas.'
        ),
        responses={204: OpenApiResponse(description='Conta excluída.')},
    ),
)
class MeView(APIView):
    """Consulta, altera e exclui a conta do usuário logado."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def delete(self, request):
        # ``pre_delete`` (users.signals) marca o nome do criador nas tarefas
        # como ``[DELETADO]`` e o Django anula as FKs ``creator``/``responsible``
        # (ambas ``on_delete=SET_NULL``) e remove os tokens em cascata.
        request.user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

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


@extend_schema(
    summary='Troca a senha',
    description=(
        'Troca a senha do usuário autenticado. É necessário informar a senha atual; '
        'a nova senha precisa ter no mínimo 8 caracteres. Os tokens existentes são '
        'invalidados, exigindo novo login.'
    ),
    request=ChangePasswordSerializer,
    responses={200: _detail_response('Senha alterada')},
    examples=[
        OpenApiExample(
            'Troca de senha',
            value={
                'current_password': 'senha-atual-123',
                'new_password': 'nova-senha-456',
            },
            request_only=True,
        ),
    ],
)
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


@extend_schema(
    summary='Solicita recuperação de senha',
    description=(
        'Gera um token de recuperação de senha para o email informado. Em '
        'desenvolvimento, o email é enviado pelo console backend do Django, então o '
        'token aparece no terminal do servidor.'
    ),
    request=ForgotPasswordSerializer,
    responses={200: _detail_response('Email de recuperação enviado')},
    examples=[
        OpenApiExample(
            'Solicitar recuperação',
            value={'email': 'maria@exemplo.com'},
            request_only=True,
        ),
    ],
)
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


@extend_schema(
    summary='Redefine a senha por token',
    description=(
        'Redefine a senha usando o token de recuperação recebido por email. O token '
        'expira em 1 hora e só pode ser usado uma vez. A nova senha precisa ter no '
        'mínimo 8 caracteres. Os tokens de acesso existentes são invalidados.'
    ),
    request=ResetPasswordSerializer,
    responses={200: _detail_response('Senha redefinida')},
    examples=[
        OpenApiExample(
            'Redefinir senha',
            value={
                'token': 'cole-aqui-o-token-recebido',
                'new_password': 'nova-senha-456',
            },
            request_only=True,
        ),
    ],
)
class ResetPasswordView(APIView):
    """Redefine senha usando token de recuperação."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'Senha redefinida com sucesso.'})


@extend_schema_view(
    list=extend_schema(
        summary='Lista usuários',
        description='Lista todos os usuários. Restrito a administradores.',
    ),
    retrieve=extend_schema(
        summary='Detalha usuário',
        description='Retorna os dados de um usuário pelo id.',
    ),
    partial_update=extend_schema(
        summary='Atualiza usuário parcialmente',
        description=(
            'Atualiza parcialmente um usuário. Apenas administradores podem alterar '
            'o papel ("role"); usuários comuns só editam a própria conta.'
        ),
        examples=[
            OpenApiExample(
                'Promover a administrador',
                value={'role': 'ADMINISTRADOR'},
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary='Atualiza usuário',
        description='Atualiza um usuário. Apenas administradores podem alterar o papel ("role").',
    ),
    destroy=extend_schema(
        summary='Exclui usuário',
        description='Exclui um usuário. Restrito ao próprio usuário ou a um administrador.',
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """Gerenciamento de usuários."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdministrador()]

        if self.action in ('retrieve', 'partial_update', 'update', 'destroy'):
            return [permissions.IsAuthenticated(), IsSelfOrAdministrador()]

        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        request_user = self.request.user

        if request_user.role != User.Role.ADMINISTRADOR:
            serializer.validated_data.pop('role', None)

        serializer.save()