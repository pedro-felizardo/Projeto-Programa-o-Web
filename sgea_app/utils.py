from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .tokens import token_ativacao
from .models import RegistroAuditoria

def enviar_email_confirmacao(usuario, request):
    token = token_ativacao.make_token(usuario)
    uid = usuario.pk

    link = request.build_absolute_uri(
        reverse("confirmar_email", args=[uid, token])
    )

    assunto = "Confirmação de Cadastro - SGEA"

    mensagem = f"""
Olá {usuario.nome}, seja bem-vindo ao SGEA!

Clique no link abaixo para ativar sua conta:

{link}

Se você não fez este cadastro, ignore este e-mail.
    """

    html = f"""
<h2>Bem-vindo ao SGEA, {usuario.nome}!</h2>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/SGEA_logo.png/600px-SGEA_logo.png" width="200">

<p>Para ativar sua conta, clique no botão abaixo:</p>

<p>
<a href="{link}"
style="padding:12px 20px;background:#005bbb;color:white;text-decoration:none;border-radius:6px;">
Ativar Conta
</a>
</p>

<p>Ou abra este link no navegador:</p>
<p>{link}</p>
"""

    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        html_message=html
    )

def log_auditoria(usuario, acao):
    """
    Função auxiliar para registrar uma ação crítica no banco de dados.
    """
    try:
        # Cria o registro, aceitando usuario=None para ações do sistema/deslogadas
        RegistroAuditoria.objects.create(usuario=usuario, acao=acao)
    except Exception as e:
        # Em caso de erro de log, apenas printa (não deve quebrar a requisição principal)
        print(f"ERRO DE LOG DE AUDITORIA: {e}") 
        pass