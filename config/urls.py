"""Configuração de URLs raiz do projeto.

Agrega as rotas de todas as aplicações e da documentação da API. Encaminha o
prefixo ``tasks/`` para o app de tarefas e expõe o schema OpenAPI e a interface
Swagger.

Rotas de nível raiz:
    - ``admin/``       -> site administrativo do Django.
    - ``tasks/``       -> CRUD de tarefas.
    - ``users/``       -> consulta de usuários (descoberta de papel).
    - ``schema/``      -> schema OpenAPI (YAML/JSON) gerado pelo drf-spectacular.
    - ``swagger/``     -> interface Swagger UI navegável.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')),
    # Documentação da API (drf-spectacular).
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
