from django.urls import path
from .views import confirmar_email
from . import views

urlpatterns = [
    # Rotas Públicas (Sem necessidade de login)
    path('', views.lista_eventos, name='home'),             # Lista de eventos (Página inicial)
    path('evento/<int:evento_id>/', views.detalhe_evento, name='detalhe_evento'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),
    
    # Rotas de Login e Logout
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Rotas de Usuário Autenticado (Aluno/Professor/Organizador)
    path('dashboard/', views.dashboard, name='dashboard'), # Página inicial após login
    path('inscrever/<int:evento_id>/', views.inscrever_evento, name='inscrever_evento'),
    path('evento/<int:evento_id>/desinscrever/', views.desinscrever_evento, name='desinscrever_evento'),
    path('meus_certificados/', views.meus_certificados, name='meus_certificados'),
    
    # Rotas de Organizador (Requer perfil 'Organizador')
    path('eventos/novo/', views.criar_evento, name='criar_evento'),
    path('eventos/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('evento/<int:evento_id>/inscritos/', views.lista_inscritos, name='lista_inscritos'),
    path('evento/<int:evento_id>/emitir_certificados/', views.emitir_certificados, name='emitir_certificados'),
    path('auditoria/', views.registros_auditoria, name='registros_auditoria'),

    # Rota da confirmação por e-mail
    path("confirmar-email/<int:uid>/<str:token>/", confirmar_email, name="confirmar_email"),
]
