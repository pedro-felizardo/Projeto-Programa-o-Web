from django.urls import reverse
from .tokens import token_ativacao
from .models import RegistroAuditoria

def enviar_email_confirmacao(usuario, request):
    """
    Agora NÃO envia e-mail de verdade.
    Apenas SIMULA no terminal.
    """
    token = token_ativacao.make_token(usuario)
    uid = usuario.pk

    link = request.build_absolute_uri(
        reverse("confirmar_email", args=[uid, token])
    )

    print("\n================ EMAIL SIMULADO ================")
    print(f"📨 Assunto: Confirmação de Cadastro - SGEA")
    print(f"👤 Para: {usuario.email}")
    print("-----------------------------------------------")
    print(f"Olá {usuario.nome}, seja bem-vindo ao SGEA!\n")
    print(f"Clique no link abaixo para ativar sua conta:\n{link}\n")
    print("Se você não fez este cadastro, apenas ignore.")
    print("===============================================\n")

    # Lógica de tokens, ativação e fluxo permanece igual.

def log_auditoria(usuario, acao):
    try:
        RegistroAuditoria.objects.create(usuario=usuario, acao=acao)
    except Exception as e:
        print(f"ERRO DE LOG DE AUDITORIA: {e}")
        pass
